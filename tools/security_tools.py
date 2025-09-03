#!/usr/bin/env python3
"""
Security tools with AES-256-GCM encryption and compliance features.

This module provides AES-256-GCM encryption with PBKDF2 key derivation,
tamper-evident audit trails, and GDPR/HIPAA compliance features.
"""

import base64
import hashlib
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class AESGCMEncryptor:
    """AES-256-GCM encryption with PBKDF2 key derivation."""

    def __init__(self, audit_log_path: Optional[str] = None):
        self.audit_log_path = Path(audit_log_path) if audit_log_path else Path(".mcp_audit.log")
        self.audit_log_path.parent.mkdir(exist_ok=True)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive AES-256 key using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # As specified in requirements
        )
        return kdf.derive(password.encode())

    def _log_audit_event(
        self, operation: str, actor: str, target: str, compliance_tags: List[str]
    ) -> None:
        """Log tamper-evident audit event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "actor": actor,
            "target": target,
            "compliance_tags": compliance_tags,
            "hash_chain": self._get_last_hash(),
        }

        # Calculate hash of this event
        event_str = json.dumps(event, sort_keys=True)
        event_hash = hashlib.sha256(event_str.encode()).hexdigest()
        event["event_hash"] = event_hash

        # Append to audit log
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def _get_last_hash(self) -> str:
        """Get hash of last audit event for tamper-evident chain."""
        if not self.audit_log_path.exists():
            return "genesis"

        with open(self.audit_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return "genesis"

            last_event = json.loads(lines[-1])
            return str(last_event.get("event_hash", "genesis"))

    def encrypt(self, data: str, password: str, data_type: str = "general") -> Dict[str, Any]:
        """Encrypt data using AES-256-GCM."""
        # Generate salt and IV
        salt = secrets.token_bytes(16)  # 128 bits
        iv = secrets.token_bytes(12)  # 96 bits for GCM

        # Derive key
        key = self._derive_key(password, salt)

        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        tag = encryptor.tag

        # Combine: salt + iv + ciphertext + tag
        encrypted_data = salt + iv + ciphertext + tag
        encoded = base64.b64encode(encrypted_data).decode()

        # Log audit event
        self._log_audit_event(
            operation="encrypt",
            actor="mcp_server",
            target=f"data_type:{data_type}",
            compliance_tags=self._get_compliance_tags(data_type),
        )

        return {
            "encrypted_data": encoded,
            "salt": base64.b64encode(salt).decode(),
            "iv": base64.b64encode(iv).decode(),
            "tag": base64.b64encode(tag).decode(),
        }

    def decrypt(
        self, encrypted_data: str, password: str, data_type: str = "general"
    ) -> Dict[str, Any]:
        """Decrypt data using AES-256-GCM."""
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data)

            # Extract components
            salt = encrypted_bytes[:16]
            iv = encrypted_bytes[16:28]
            ciphertext = encrypted_bytes[28:-16]
            tag = encrypted_bytes[-16:]

            # Derive key
            key = self._derive_key(password, salt)

            # Decrypt
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Log audit event
            self._log_audit_event(
                operation="decrypt",
                actor="mcp_server",
                target=f"data_type:{data_type}",
                compliance_tags=self._get_compliance_tags(data_type),
            )

            return {"decrypted_data": plaintext.decode()}

        except Exception as e:
            return {"error": f"Decryption failed: {str(e)}"}

    def _get_compliance_tags(self, data_type: str) -> List[str]:
        """Get compliance tags based on data type."""
        tags = []
        if data_type == "pii":
            tags.extend(["GDPR", "data_protection"])
        elif data_type == "phi":
            tags.extend(["HIPAA", "health_data"])
        elif data_type == "financial":
            tags.extend(["PCI_DSS", "financial_data"])
        return tags


class EncryptSensitiveDataTool(IntelligentToolBase):
    """Encrypt sensitive data with AES-256-GCM."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None):
        super().__init__(project_path, security_manager)
        self.encryptor = AESGCMEncryptor(str(Path(project_path) / ".mcp_audit.log"))

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Determine operation from tool name
        tool_name = context.tool_name
        if tool_name == "securityEncryptData":
            operation = "encrypt"
        elif tool_name == "securityDecryptData":
            operation = "decrypt"
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        data_ref = arguments.get("dataRef")

        if not data_ref:
            return {"success": False, "error": "No dataRef provided"}

        # Extract data from dataRef
        data_type = data_ref.get("type")
        data_value = data_ref.get("value")

        if data_type == "inline":
            data = data_value
        elif data_type == "path":
            # Read from file
            try:
                with open(data_value, "r", encoding="utf-8") as f:
                    data = f.read()
            except Exception as e:
                return {"success": False, "error": f"Failed to read file: {e}"}
        else:
            return {"success": False, "error": f"Unsupported dataRef type: {data_type}"}

        # Use a default password for demo (in production, this should be securely managed)
        password = arguments.get("password", "default_mcp_password")

        if operation == "encrypt":
            result = self.encryptor.encrypt(data, password, "general")
            if "error" in result:
                return {"success": False, "error": result["error"]}

            # Generate audit ID
            import uuid

            audit_id = f"audit-{datetime.now().strftime('%Y-%m-%d')}-{str(uuid.uuid4())[:8]}"

            return {
                "encryptedRef": {"type": "inline", "value": result["encrypted_data"]},
                "auditId": audit_id,
            }
        elif operation == "decrypt":
            result = self.encryptor.decrypt(data, password, "general")
            if "error" in result:
                return {"success": False, "error": result["error"]}

            # Generate audit ID
            import uuid

            audit_id = f"audit-{datetime.now().strftime('%Y-%m-%d')}-{str(uuid.uuid4())[:8]}"

            return {
                "plaintextRef": {"type": "inline", "value": result["decrypted_data"]},
                "auditId": audit_id,
            }
        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}


class SecurityAuditTrailTool(IntelligentToolBase):
    """Query tamper-evident audit trail with hash chaining."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None):
        super().__init__(project_path, security_manager)
        self.audit_log_path = Path(project_path) / ".mcp_audit.log"

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 50)

        if not self.audit_log_path.exists():
            return {"events": []}

        events = []
        with open(self.audit_log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        if self._matches_filters(event, filters):
                            events.append(
                                {
                                    "time": event.get("timestamp"),
                                    "actor": event.get("actor", "unknown"),
                                    "op": event.get("operation"),
                                    "target": event.get("target"),
                                    "result": "success",  # Assume success if logged
                                    "complianceTags": event.get("compliance_tags", []),
                                    "prevHash": event.get("hash_chain", "genesis"),
                                    "hash": event.get("event_hash"),
                                }
                            )
                    except json.JSONDecodeError:
                        continue

        # Sort by time descending and limit
        events.sort(key=lambda x: x["time"], reverse=True)
        return {"events": events[:limit]}

    def _matches_filters(self, event: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if event matches the given filters."""
        for key, value in filters.items():
            if key == "subjectId":
                # Check if subjectId appears in target
                if value not in event.get("target", ""):
                    return False
            elif key == "op":
                if event.get("operation") != value:
                    return False
            elif key == "dateRange":
                # Date filtering would require parsing timestamps
                # For now, skip date filtering
                pass
        return True


class SecureStorageTool(IntelligentToolBase):
    """Secure storage with encryption and compliance."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None):
        super().__init__(project_path, security_manager)
        self.project_path = Path(project_path)

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        storage_type = arguments.get("storage_type", "shared_preferences")
        encryption_level = arguments.get("encryption_level", "standard")
        compliance_mode = arguments.get("compliance_mode", "none")

        recommendations = self._get_storage_recommendations(
            str(storage_type), str(encryption_level), str(compliance_mode)
        )

        return {
            "success": True,
            "storage_type": storage_type,
            "encryption_level": encryption_level,
            "compliance_mode": compliance_mode,
            "recommendations": recommendations,
            "implementation_guide": self._get_implementation_guide(str(storage_type)),
        }

    def _get_storage_recommendations(
        self, storage_type: str, encryption_level: str, compliance_mode: str
    ) -> List[str]:
        """Get storage recommendations based on type and compliance."""
        recommendations = []

        if storage_type == "shared_preferences":
            recommendations.extend(
                [
                    "Use EncryptedSharedPreferences for automatic encryption",
                    "Avoid storing sensitive data in SharedPreferences",
                    "Consider migrating to more secure storage",
                ]
            )
        elif storage_type == "room":
            recommendations.extend(
                [
                    "Use SQLCipher for database encryption",
                    "Implement proper key management",
                    "Regular backup with encryption",
                ]
            )
        elif storage_type == "keystore":
            recommendations.extend(
                [
                    "Use Android Keystore for cryptographic keys",
                    "Avoid exporting keys from Keystore",
                    "Implement key rotation policies",
                ]
            )
        elif storage_type == "file":
            recommendations.extend(
                [
                    "Encrypt files before storage",
                    "Use secure file permissions",
                    "Implement file integrity checks",
                ]
            )

        # Add encryption level recommendations
        if encryption_level == "high":
            recommendations.append("Use AES-256-GCM for all encryption operations")
        elif encryption_level == "maximum":
            recommendations.extend(
                [
                    "Use hardware-backed keystore when available",
                    "Implement biometric authentication",
                    "Use certificate pinning for network operations",
                ]
            )

        # Add compliance recommendations
        if compliance_mode == "gdpr":
            recommendations.extend(
                [
                    "Implement data minimization principles",
                    "Provide user consent mechanisms",
                    "Support right to erasure",
                ]
            )
        elif compliance_mode == "hipaa":
            recommendations.extend(
                [
                    "Implement audit logging for all data access",
                    "Use role-based access control",
                    "Regular security assessments",
                ]
            )

        return recommendations

    def _get_implementation_guide(self, storage_type: str) -> Dict[str, Any]:
        """Get implementation guide for storage type."""
        guides = {
            "shared_preferences": {
                "dependencies": ["androidx.security:security-crypto:1.1.0-alpha06"],
                "code_example": """
// EncryptedSharedPreferences usage
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val sharedPreferences = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
""",
            },
            "room": {
                "dependencies": ["net.zetetic:android-database-sqlcipher:4.5.4"],
                "code_example": """
// SQLCipher with Room
val passphrase = SQLiteDatabase.getBytes("your-passphrase".toCharArray())
val factory = SupportFactory(passphrase)

val db = Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .openHelperFactory(factory)
    .build()
""",
            },
        }

        return guides.get(storage_type, {"message": "Implementation guide not available"})
