"""File management operations for Kotlin MCP Server.

Provides backup, restore, sync, encryption/decryption, and organization
capabilities with audit logging. Supports both local and cloud (S3) paths
and uses async locks to ensure safe concurrency.
"""

from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import aiofiles

try:  # Optional dependency for cloud operations
    import boto3
except Exception:  # pragma: no cover - boto3 optional
    boto3 = None

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext
from utils.security import SecurityManager, decrypt_data, encrypt_data


class FileManagementTool(IntelligentToolBase):
    """Advanced file management operations with audit logging."""

    def __init__(self, project_path: str, security_manager: Optional[SecurityManager] = None) -> None:
        super().__init__(project_path, security_manager)
        self._lock = asyncio.Lock()

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dispatch file management operations based on arguments."""

        operation = arguments.get("operation")
        target = arguments.get("target_path")
        destination = arguments.get("destination")
        key = arguments.get("key")

        if not operation or not target:
            return {"success": False, "error": "operation and target_path are required"}

        if operation == "backup":
            return await self._backup(target, destination)
        if operation == "restore":
            return await self._restore(target, destination)
        if operation == "sync":
            return await self._sync(target, destination)
        if operation == "encrypt":
            if not key:
                return {"success": False, "error": "encryption key required"}
            return await self._encrypt_file(target, key, destination)
        if operation == "decrypt":
            if not key:
                return {"success": False, "error": "decryption key required"}
            return await self._decrypt_file(target, key, destination)
        if operation == "organize":
            return await self._organize(target)

        return {"success": False, "error": f"Unsupported operation: {operation}"}

    # ------------------------------------------------------------------
    async def _backup(self, target_path: str, destination: Optional[str]) -> Dict[str, Any]:
        """Backup a local path to a destination (local or cloud)."""
        if not destination:
            return {"success": False, "error": "destination required for backup"}

        async with self._lock:
            src = self._resolve_local(target_path)
            if src is None:
                return {"success": False, "error": "invalid target path"}

            self.security_manager.log_audit_event("backup", str(src), destination)

            if self._is_cloud(destination):
                if boto3 is None:
                    return {"success": False, "error": "boto3 not installed for cloud operations"}
                await self._upload_to_s3(src, destination)
            else:
                dest = self._resolve_local(destination)
                if dest is None:
                    return {"success": False, "error": "invalid destination"}
                await self._copy_local(src, dest)

        return {"success": True, "operation": "backup", "target": str(src), "destination": destination}

    async def _restore(self, backup_path: str, destination: Optional[str]) -> Dict[str, Any]:
        """Restore a backup from local or cloud path to destination."""
        if not destination:
            return {"success": False, "error": "destination required for restore"}

        async with self._lock:
            dest = self._resolve_local(destination)
            if dest is None:
                return {"success": False, "error": "invalid destination"}

            self.security_manager.log_audit_event("restore", backup_path, str(dest))

            if self._is_cloud(backup_path):
                if boto3 is None:
                    return {"success": False, "error": "boto3 not installed for cloud operations"}
                await self._download_from_s3(backup_path, dest)
            else:
                src = self._resolve_local(backup_path)
                if src is None:
                    return {"success": False, "error": "invalid backup path"}
                await self._copy_local(src, dest)

        return {"success": True, "operation": "restore", "source": backup_path, "destination": str(dest)}

    async def _sync(self, source: str, destination: Optional[str]) -> Dict[str, Any]:
        """Synchronize files between source and destination."""
        if not destination:
            return {"success": False, "error": "destination required for sync"}

        async with self._lock:
            self.security_manager.log_audit_event("sync", source, destination)
            if self._is_cloud(source) and not self._is_cloud(destination):
                if boto3 is None:
                    return {"success": False, "error": "boto3 not installed for cloud operations"}
                dest = self._resolve_local(destination)
                if dest is None:
                    return {"success": False, "error": "invalid destination"}
                await self._download_from_s3(source, dest)
            elif self._is_cloud(destination) and not self._is_cloud(source):
                if boto3 is None:
                    return {"success": False, "error": "boto3 not installed for cloud operations"}
                src = self._resolve_local(source)
                if src is None:
                    return {"success": False, "error": "invalid source"}
                await self._upload_to_s3(src, destination)
            else:
                src = self._resolve_local(source)
                dest = self._resolve_local(destination)
                if src is None or dest is None:
                    return {"success": False, "error": "invalid path"}
                await self._copy_local(src, dest)

        return {"success": True, "operation": "sync", "source": source, "destination": destination}

    async def _encrypt_file(
        self, target_path: str, key: str, destination: Optional[str]
    ) -> Dict[str, Any]:
        """Encrypt a file to destination or in-place."""
        async with self._lock:
            src = self._resolve_local(target_path)
            if src is None or not src.is_file():
                return {"success": False, "error": "invalid target file"}

            dest = self._resolve_local(destination) if destination else src.with_suffix(src.suffix + ".enc")
            dest.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(src, "rb") as f:
                data = await f.read()
            encrypted = encrypt_data(data, key.encode("utf-8"))
            async with aiofiles.open(dest, "wb") as f:
                await f.write(encrypted)

            self.security_manager.log_audit_event("encrypt", str(src), str(dest))

        return {"success": True, "operation": "encrypt", "output": str(dest)}

    async def _decrypt_file(
        self, target_path: str, key: str, destination: Optional[str]
    ) -> Dict[str, Any]:
        """Decrypt an encrypted file to destination or in-place."""
        async with self._lock:
            src = self._resolve_local(target_path)
            if src is None or not src.is_file():
                return {"success": False, "error": "invalid target file"}

            dest = self._resolve_local(destination) if destination else src.with_suffix(".dec")
            dest.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(src, "rb") as f:
                data = await f.read()
            decrypted = decrypt_data(data, key.encode("utf-8"))
            async with aiofiles.open(dest, "wb") as f:
                await f.write(decrypted)

            self.security_manager.log_audit_event("decrypt", str(src), str(dest))

        return {"success": True, "operation": "decrypt", "output": str(dest)}

    async def _organize(self, target_path: str) -> Dict[str, Any]:
        """Organize files in a directory by extension."""
        async with self._lock:
            directory = self._resolve_local(target_path)
            if directory is None or not directory.is_dir():
                return {"success": False, "error": "invalid directory"}

            self.security_manager.log_audit_event("organize", str(directory))

            for item in directory.iterdir():
                if item.is_file():
                    ext = item.suffix[1:] if item.suffix else "no_extension"
                    target_dir = directory / ext
                    target_dir.mkdir(parents=True, exist_ok=True)
                    await asyncio.to_thread(shutil.move, item, target_dir / item.name)

        return {"success": True, "operation": "organize", "directory": str(directory)}

    # ------------------------------------------------------------------
    def _resolve_local(self, path: Optional[str]) -> Optional[Path]:
        if not path:
            return None
        resolved = (self.project_path / path).resolve()
        try:
            resolved.relative_to(self.project_path)
        except ValueError:
            return None
        return resolved

    @staticmethod
    def _is_cloud(path: str) -> bool:
        return path.startswith("s3://")

    async def _copy_local(self, src: Path, dest: Path) -> None:
        if src.is_dir():
            await asyncio.to_thread(shutil.copytree, src, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(shutil.copy2, src, dest)

    async def _upload_to_s3(self, src: Path, s3_path: str) -> None:  # pragma: no cover - network
        bucket, key = self._parse_s3(s3_path)
        s3 = boto3.client("s3")
        if src.is_dir():
            for file in src.rglob("*"):
                if file.is_file():
                    rel_key = os.path.join(key, str(file.relative_to(src)))
                    await asyncio.to_thread(s3.upload_file, str(file), bucket, rel_key)
        else:
            await asyncio.to_thread(s3.upload_file, str(src), bucket, key)

    async def _download_from_s3(self, s3_path: str, dest: Path) -> None:  # pragma: no cover - network
        bucket, key = self._parse_s3(s3_path)
        s3 = boto3.client("s3")
        if key.endswith("/"):
            paginator = s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket, Prefix=key):
                for obj in page.get("Contents", []):
                    rel = obj["Key"][len(key) :]
                    target_file = dest / rel
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    await asyncio.to_thread(s3.download_file, bucket, obj["Key"], str(target_file))
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(s3.download_file, bucket, key, str(dest))

    @staticmethod
    def _parse_s3(s3_path: str) -> tuple[str, str]:
        path = s3_path.replace("s3://", "", 1)
        bucket, _, key = path.partition("/")
        return bucket, key
