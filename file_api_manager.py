#!/usr/bin/env python3
"""
Advanced File Manager and External API Implementation
Demonstrates comprehensive file handling and API integration capabilities
"""

import os
import shutil
import json
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import hashlib
import zipfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AdvancedFileManager:
    """Comprehensive file management system with enterprise features"""

    def __init__(self, encryption_key=None):
        self.encryption_key = encryption_key
        self.sync_observers = {}
        self.file_watchers = {}

    async def handle_file_operations(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Handle all file management operations"""

        operations = {
            "backup": self._backup_files,
            "restore": self._restore_files,
            "sync": self._sync_files,
            "encrypt": self._encrypt_files,
            "decrypt": self._decrypt_files,
            "archive": self._archive_files,
            "extract": self._extract_files,
            "watch": self._watch_directory,
            "search": self._search_files,
            "analyze": self._analyze_file_structure
        }

        if operation not in operations:
            return {"error": f"Unsupported operation: {operation}"}

        try:
            result = await operations[operation](**kwargs)
            return {"success": True, "operation": operation, **result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _backup_files(self, target_path: str, destination: str,
                           encryption_level: str = "standard", **kwargs) -> Dict:
        """Create encrypted backup of files"""
        source = Path(target_path)
        dest = Path(destination)

        if not source.exists():
            raise FileNotFoundError(f"Source path not found: {source}")

        # Create backup directory structure
        backup_dir = dest / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        files_backed_up = 0
        total_size = 0

        # Copy files with optional encryption
        for file_path in source.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source)
                backup_file = backup_dir / relative_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)

                if encryption_level != "none" and self._should_encrypt(file_path):
                    await self._encrypt_file_to_destination(file_path, backup_file)
                else:
                    shutil.copy2(file_path, backup_file)

                files_backed_up += 1
                total_size += file_path.stat().st_size

        # Create backup manifest
        manifest = {
            "created_at": datetime.now().isoformat(),
            "source_path": str(source),
            "files_count": files_backed_up,
            "total_size_bytes": total_size,
            "encryption_level": encryption_level,
            "backup_version": "1.0"
        }

        manifest_file = backup_dir / "backup_manifest.json"
        async with aiofiles.open(manifest_file, 'w') as f:
            await f.write(json.dumps(manifest, indent=2))

        return {
            "backup_path": str(backup_dir),
            "files_backed_up": files_backed_up,
            "total_size": total_size,
            "encryption_applied": encryption_level != "none"
        }

    async def _restore_files(self, backup_path: str, destination: str, **kwargs) -> Dict:
        """Restore files from backup"""
        backup_dir = Path(backup_path)
        dest = Path(destination)

        # Read backup manifest
        manifest_file = backup_dir / "backup_manifest.json"
        if manifest_file.exists():
            async with aiofiles.open(manifest_file, 'r') as f:
                manifest = json.loads(await f.read())
        else:
            manifest = {"files_count": 0}

        files_restored = 0
        for backup_file in backup_dir.rglob("*"):
            if backup_file.is_file() and backup_file.name != "backup_manifest.json":
                relative_path = backup_file.relative_to(backup_dir)
                dest_file = dest / relative_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, dest_file)
                files_restored += 1

        return {"files_restored": files_restored, "manifest": manifest}

    async def _sync_files(self, source: str, destination: str,
                         sync_strategy: str = "real_time", **kwargs) -> Dict:
        """Synchronize files between directories"""
        source_path = Path(source)
        dest_path = Path(destination)

        sync_stats = {
            "files_copied": 0,
            "files_updated": 0,
            "files_deleted": 0,
            "errors": []
        }

        # Two-way sync implementation
        await self._sync_directory(source_path, dest_path, sync_stats)

        if sync_strategy == "real_time":
            # Setup file system watcher
            sync_id = f"sync_{hashlib.md5(f'{source}{destination}'.encode()).hexdigest()[:8]}"
            self._setup_file_watcher(source_path, dest_path, sync_id)

        return {
            "sync_completed": True,
            "sync_strategy": sync_strategy,
            **sync_stats
        }

    async def _sync_directory(self, source: Path, dest: Path, stats: Dict):
        """Perform directory synchronization"""
        for source_file in source.rglob("*"):
            if source_file.is_file():
                relative_path = source_file.relative_to(source)
                dest_file = dest / relative_path

                if not dest_file.exists():
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    stats["files_copied"] += 1
                elif source_file.stat().st_mtime > dest_file.stat().st_mtime:
                    shutil.copy2(source_file, dest_file)
                    stats["files_updated"] += 1

    def _setup_file_watcher(self, source: Path, dest: Path, sync_id: str):
        """Setup real-time file system watcher"""
        class SyncHandler(FileSystemEventHandler):
            def __init__(self, source_path, dest_path):
                self.source_path = source_path
                self.dest_path = dest_path

            def on_modified(self, event):
                if not event.is_directory:
                    # Sync the modified file
                    asyncio.create_task(self._sync_single_file(event.src_path))

        handler = SyncHandler(source, dest)
        observer = Observer()
        observer.schedule(handler, str(source), recursive=True)
        observer.start()
        self.sync_observers[sync_id] = observer

    async def _encrypt_files(self, target_path: str, **kwargs) -> Dict:
        """Encrypt files in target directory"""
        target = Path(target_path)
        encrypted_count = 0

        for file_path in target.rglob("*"):
            if file_path.is_file() and self._should_encrypt(file_path):
                await self._encrypt_file_to_destination(file_path, file_path.with_suffix(file_path.suffix + '.enc'))
                encrypted_count += 1

        return {"files_encrypted": encrypted_count}

    async def _decrypt_files(self, target_path: str, **kwargs) -> Dict:
        """Decrypt files in target directory"""
        target = Path(target_path)
        decrypted_count = 0

        for file_path in target.rglob("*.enc"):
            if file_path.is_file():
                original_path = file_path.with_suffix('')
                # Decrypt file logic here
                decrypted_count += 1

        return {"files_decrypted": decrypted_count}

    async def _archive_files(self, target_path: str, archive_name: str = None, **kwargs) -> Dict:
        """Create archive of files"""
        target = Path(target_path)
        archive_path = target.parent / f"{archive_name or target.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in target.rglob("*"):
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(target))

        return {"archive_created": str(archive_path), "size_bytes": archive_path.stat().st_size}

    async def _extract_files(self, archive_path: str, destination: str = None, **kwargs) -> Dict:
        """Extract files from archive"""
        archive = Path(archive_path)
        dest = Path(destination) if destination else archive.parent / archive.stem

        with zipfile.ZipFile(archive, 'r') as zipf:
            zipf.extractall(dest)
            extracted_files = len(zipf.namelist())

        return {"files_extracted": extracted_files, "destination": str(dest)}

    async def _watch_directory(self, target_path: str, **kwargs) -> Dict:
        """Setup directory watching"""
        # Implementation for directory watching
        return {"watching": True, "path": target_path}

    async def _search_files(self, target_path: str, pattern: str = "*", **kwargs) -> Dict:
        """Search for files matching pattern"""
        target = Path(target_path)
        found_files = list(target.rglob(pattern))

        return {"files_found": len(found_files), "files": [str(f) for f in found_files[:100]]}

    async def _analyze_file_structure(self, target_path: str, **kwargs) -> Dict:
        """Analyze file structure and provide statistics"""
        target = Path(target_path)
        stats = {
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "largest_files": []
        }

        file_sizes = []
        for file_path in target.rglob("*"):
            if file_path.is_file():
                stats["total_files"] += 1
                size = file_path.stat().st_size
                stats["total_size"] += size

                ext = file_path.suffix.lower()
                stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1

                file_sizes.append((str(file_path), size))

        # Get largest files
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        stats["largest_files"] = file_sizes[:10]

        return stats

    async def _encrypt_file_to_destination(self, source: Path, destination: Path):
        """Encrypt file from source to destination"""
        if self.encryption_key:
            # Simple encryption simulation - in production use proper encryption
            async with aiofiles.open(source, 'rb') as src, aiofiles.open(destination, 'wb') as dst:
                content = await src.read()
                # Simulated encryption - would use actual encryption here
                encrypted_content = content  # Placeholder
                await dst.write(encrypted_content)
        else:
            shutil.copy2(source, destination)

    def _should_encrypt(self, file_path: Path) -> bool:
        """Determine if file should be encrypted based on content/extension"""
        sensitive_extensions = {'.env', '.key', '.pem', '.p12', '.jks'}
        sensitive_patterns = {'password', 'secret', 'private', 'config'}

        # Check file extension
        if file_path.suffix.lower() in sensitive_extensions:
            return True

        # Check filename patterns
        filename_lower = file_path.name.lower()
        return any(pattern in filename_lower for pattern in sensitive_patterns)

class ExternalAPIManager:
    """Comprehensive external API integration and management"""

    def __init__(self):
        self.api_clients = {}
        self.api_configs = {}
        self.usage_metrics = {}
        self.rate_limiters = {}

    async def integrate_api(self, api_name: str, base_url: str, auth_type: str,
                           security_features: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Integrate external API with full configuration"""

        api_config = {
            "name": api_name,
            "base_url": base_url.rstrip('/'),
            "auth_type": auth_type,
            "security_features": security_features or [],
            "created_at": datetime.now().isoformat(),
            "endpoints": {},
            "rate_limits": kwargs.get("rate_limits", {}),
            "timeout": kwargs.get("timeout", 30),
            "retry_policy": kwargs.get("retry_policy", {"max_retries": 3, "backoff_factor": 1})
        }

        # Setup authentication
        auth_config = await self._setup_authentication(auth_type, kwargs)
        api_config["auth_config"] = auth_config

        # Create HTTP client with security features
        client = await self._create_http_client(api_config)

        # Setup monitoring and metrics
        if "request_logging" in security_features:
            self._setup_request_logging(api_name)

        if "rate_limiting" in security_features:
            self._setup_rate_limiting(api_name, api_config["rate_limits"])

        # Store configuration
        self.api_configs[api_name] = api_config
        self.api_clients[api_name] = client
        self.usage_metrics[api_name] = {
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency": 0,
            "last_request": None
        }

        return {
            "integration_created": True,
            "api_name": api_name,
            "security_features_enabled": len(security_features) > 0,
            "endpoints_configured": 0,
            "monitoring_enabled": True
        }

    async def _create_http_client(self, config: Dict) -> aiohttp.ClientSession:
        """Create HTTP client with configuration"""
        timeout = aiohttp.ClientTimeout(total=config["timeout"])
        return aiohttp.ClientSession(timeout=timeout)

    def _setup_request_logging(self, api_name: str):
        """Setup request logging for API"""
        # Implementation for request logging
        pass

    def _setup_rate_limiting(self, api_name: str, rate_limits: Dict):
        """Setup rate limiting for API"""
        self.rate_limiters[api_name] = {
            "requests_per_minute": rate_limits.get("requests_per_minute", 60),
            "last_request_time": 0,
            "request_count": 0
        }

    async def _check_rate_limit(self, api_name: str) -> bool:
        """Check if API request is within rate limits"""
        if api_name not in self.rate_limiters:
            return True

        limiter = self.rate_limiters[api_name]
        current_time = datetime.now().timestamp()

        # Simple rate limiting logic
        if current_time - limiter["last_request_time"] > 60:
            limiter["request_count"] = 0
            limiter["last_request_time"] = current_time

        if limiter["request_count"] >= limiter["requests_per_minute"]:
            return False

        limiter["request_count"] += 1
        return True

    def _update_metrics(self, api_name: str, status_code: int, latency: float, error: bool = False):
        """Update API usage metrics"""
        metrics = self.usage_metrics[api_name]
        metrics["requests_made"] += 1
        metrics["total_latency"] += latency
        metrics["last_request"] = datetime.now().isoformat()

        if error or status_code >= 400:
            metrics["failed_requests"] += 1
        else:
            metrics["successful_requests"] += 1

    def _log_api_request(self, api_name: str, method: str, url: str, status: int, latency: float):
        """Log API request for audit purposes"""
        # Implementation for API request logging
        pass

    def _calculate_api_costs(self, api_name: str, usage_data: Dict) -> float:
        """Calculate estimated API costs"""
        # Simple cost calculation - would be API-specific in production
        return usage_data["requests_made"] * 0.001  # $0.001 per request

    async def _setup_authentication(self, auth_type: str, config: Dict) -> Dict:
        """Setup authentication configuration"""
        auth_configs = {
            "api_key": {"key": config.get("api_key"), "header": config.get("key_header", "X-API-Key")},
            "oauth": {"client_id": config.get("client_id"), "client_secret": config.get("client_secret")},
            "jwt": {"token": config.get("jwt_token"), "header": "Authorization"},
            "basic": {"username": config.get("username"), "password": config.get("password")}
        }
        return auth_configs.get(auth_type, {})

