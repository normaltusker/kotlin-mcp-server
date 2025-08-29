#!/usr/bin/env python3
"""
Security tools wrapping Android Keystore APIs.

This module provides helpers for encrypting and decrypting data using the
Android Keystore when available. In non-Android environments the module falls
back to local Fernet based encryption. Tools also expose safe storage
recommendations and compliance flags to guide secure implementations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class AndroidKeystoreWrapper:
    """Wraps Android Keystore APIs with a Python fallback.

    The wrapper attempts to use real Android Keystore classes via ``pyjnius``.
    When those classes are unavailable (e.g. during server side development),
    it falls back to storing Fernet keys in a local ``.keystore`` directory.
    """

    def __init__(self) -> None:
        self._use_android_keystore = False
        try:  # pragma: no cover - Android environment rarely available in tests
            from jnius import autoclass  # type: ignore

            self._key_store = autoclass("java.security.KeyStore").getInstance("AndroidKeyStore")
            self._key_store.load(None)
            self._cipher = autoclass("javax.crypto.Cipher")
            self._key_generator = autoclass("javax.crypto.KeyGenerator")
            self._key_spec_builder = autoclass(
                "android.security.keystore.KeyGenParameterSpec$Builder"
            )
            self._key_properties = autoclass("android.security.keystore.KeyProperties")
            self._use_android_keystore = True
        except Exception:
            # Fallback: simple local key directory using Fernet keys
            self._key_dir = Path(".keystore")
            self._key_dir.mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # Key management helpers
    # ------------------------------------------------------------------
    def generate_key(self, alias: str) -> None:
        """Generate a key for the given alias."""
        if self._use_android_keystore:  # pragma: no cover
            try:
                builder = self._key_spec_builder(
                    alias,
                    self._key_properties.PURPOSE_ENCRYPT | self._key_properties.PURPOSE_DECRYPT,
                )
                builder = builder.setBlockModes(self._key_properties.BLOCK_MODE_GCM)
                builder = builder.setEncryptionPaddings(
                    self._key_properties.ENCRYPTION_PADDING_NONE
                )
                key_gen = self._key_generator.getInstance(
                    self._key_properties.KEY_ALGORITHM_AES, "AndroidKeyStore"
                )
                key_gen.init(builder.build())
                key_gen.generateKey()
                return
            except Exception:
                # If anything fails we fall back to local storage
                self._use_android_keystore = False
        # Fallback
        key_file = self._key_dir / f"{alias}.key"
        if not key_file.exists():
            key = Fernet.generate_key()
            key_file.write_bytes(key)

    def _load_key(self, alias: str) -> bytes:
        key_file = self._key_dir / f"{alias}.key"
        return key_file.read_bytes()

    def delete_key(self, alias: str) -> None:
        if self._use_android_keystore:  # pragma: no cover
            try:
                self._key_store.deleteEntry(alias)
                return
            except Exception:
                pass
        key_file = self._key_dir / f"{alias}.key"
        if key_file.exists():
            key_file.unlink()

    # ------------------------------------------------------------------
    # Encryption / Decryption helpers
    # ------------------------------------------------------------------
    def encrypt(self, alias: str, data: bytes) -> bytes:
        if self._use_android_keystore:  # pragma: no cover
            try:
                secret_key = self._key_store.getKey(alias, None)
                cipher = self._cipher.getInstance("AES/GCM/NoPadding")
                cipher.init(self._cipher.ENCRYPT_MODE, secret_key)
                iv = bytes(cipher.getIV())
                encrypted = bytes(cipher.doFinal(data))
                return iv + encrypted
            except Exception:
                self._use_android_keystore = False
        if not (self._key_dir / f"{alias}.key").exists():
            self.generate_key(alias)
        key = self._load_key(alias)
        f = Fernet(key)
        return f.encrypt(data)

    def decrypt(self, alias: str, token: bytes) -> bytes:
        if self._use_android_keystore:  # pragma: no cover
            try:
                from jnius import autoclass  # type: ignore

                secret_key = self._key_store.getKey(alias, None)
                cipher = self._cipher.getInstance("AES/GCM/NoPadding")
                iv, enc = token[:12], token[12:]
                gcm_spec_cls = autoclass("javax.crypto.spec.GCMParameterSpec")
                spec = gcm_spec_cls(128, iv)
                cipher.init(self._cipher.DECRYPT_MODE, secret_key, spec)
                return bytes(cipher.doFinal(enc))
            except Exception:
                self._use_android_keystore = False
        key = self._load_key(alias)
        f = Fernet(key)
        return f.decrypt(token)

    # ------------------------------------------------------------------
    # Recommendations and compliance
    # ------------------------------------------------------------------
    def get_storage_recommendations(self) -> List[str]:
        return [
            "Store cryptographic keys in Android Keystore",
            "Use hardware backed keystore when available",
            "Avoid persisting plaintext secrets on device",
            "Rotate keys regularly and on suspected compromise",
        ]

    def get_compliance_flags(self) -> List[str]:
        # These represent common compliance frameworks developers may target
        return ["GDPR", "HIPAA"]


class EncryptSensitiveDataTool(IntelligentToolBase):
    """Encrypt or decrypt data using the Android Keystore."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None):
        super().__init__(project_path, security_manager)
        self.keystore = AndroidKeystoreWrapper()

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        alias = arguments.get("alias", "mcp_default")
        operation = arguments.get("operation", "encrypt").lower()
        data = arguments.get("data")
        if data is None:
            return {"error": "No data provided"}

        data_bytes = data.encode("utf-8") if isinstance(data, str) else data

        if operation == "encrypt":
            token = self.keystore.encrypt(alias, data_bytes)
            result: Dict[str, Any] = {"ciphertext": token.decode("utf-8")}
        elif operation == "decrypt":
            try:
                plaintext = self.keystore.decrypt(alias, data_bytes)
            except Exception as exc:  # pragma: no cover - rare failure
                return {"error": f"Decryption failed: {exc}"}
            result = {"plaintext": plaintext.decode("utf-8")}
        else:
            return {"error": f"Unknown operation: {operation}"}

        result.update(
            {
                "alias": alias,
                "recommendations": self.keystore.get_storage_recommendations(),
                "compliance_flags": self.keystore.get_compliance_flags(),
            }
        )
        return result


class SecureStorageTool(IntelligentToolBase):
    """Provide secure storage recommendations and optional key generation."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None):
        super().__init__(project_path, security_manager)
        self.keystore = AndroidKeystoreWrapper()

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        alias = arguments.get("alias")
        if alias:
            self.keystore.generate_key(alias)
        return {
            "alias": alias,
            "recommendations": self.keystore.get_storage_recommendations(),
            "compliance_flags": self.keystore.get_compliance_flags(),
        }
