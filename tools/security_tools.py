#!/usr/bin/env python3
"""Security tools for secure storage operations.

This module provides implementations for secure storage setup using either
Room with SQLCipher encryption or EncryptedFile, with keys managed via the
Android Keystore. It also scans Kotlin source files to suggest refactors for
insecure storage usages like plain SharedPreferences or unencrypted files.
"""

from typing import Any, Dict, List

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class SetupSecureStorageTool(IntelligentToolBase):
    """Configure encrypted storage and suggest refactors for insecure usages."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        storage_type = arguments.get("storage_type", "room").lower()

        setup_code = self._generate_setup_code(storage_type)
        refactor_suggestions = await self._find_insecure_storage_usages()

        return {
            "storage_type": storage_type,
            "setup_code": setup_code,
            "refactor_suggestions": refactor_suggestions,
        }

    def _generate_setup_code(self, storage_type: str) -> str:
        """Return Kotlin snippet for requested secure storage type."""
        if storage_type == "room":
            return (
                """// Room database with SQLCipher encryption and Keystore-managed key
val keyAlias = \"room_db_key\"
val keyGenParameterSpec = KeyGenParameterSpec.Builder(
    keyAlias,
    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
).setBlockModes(KeyProperties.BLOCK_MODE_GCM)
 .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
 .setKeySize(256)
 .build()

val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, \"AndroidKeyStore\")
keyGenerator.init(keyGenParameterSpec)
val secretKey = keyGenerator.generateKey()
val passphrase = SQLiteDatabase.getBytes(secretKey.encoded)
val factory = SupportFactory(passphrase)

val db = Room.databaseBuilder(context, AppDatabase::class.java, \"secure.db\")
    .openHelperFactory(factory)
    .build()
"""
            )
        if storage_type == "encrypted_file":
            return (
                """// EncryptedFile with key stored in Android Keystore
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val file = File(context.filesDir, \"secret.txt\")
val encryptedFile = EncryptedFile.Builder(
    context,
    file,
    masterKey,
    EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
).build()

encryptedFile.openFileOutput().bufferedWriter().use {
    it.write(\"Sensitive data\")
}
"""
            )
        if storage_type == "encrypted_sharedprefs" or storage_type == "shared_preferences":
            return (
                """// EncryptedSharedPreferences backed by Android Keystore
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context,
    \"secure_prefs\",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
"""
            )
        if storage_type == "keystore":
            return (
                """// Generate and retrieve keys directly from Android Keystore
val keyGenParameterSpec = KeyGenParameterSpec.Builder(
    "app_master_key",
    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
).setBlockModes(KeyProperties.BLOCK_MODE_GCM)
 .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
 .setKeySize(256)
 .build()

val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
keyGenerator.init(keyGenParameterSpec)
val secretKey = keyGenerator.generateKey()
"""
            )
        return "// Unsupported storage type"

    async def _find_insecure_storage_usages(self) -> List[Dict[str, str]]:
        """Scan project for insecure storage patterns and suggest refactors."""
        patterns = {
            "SharedPreferences": "Replace with EncryptedSharedPreferences or secure storage.",
            "openFileOutput": "Use EncryptedFile with a Keystore-managed key.",
            "File(": "Use EncryptedFile or Room with SQLCipher.",
        }
        suggestions: List[Dict[str, str]] = []
        for path in self.project_path.rglob("*.kt"):
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                continue
            for pattern, recommendation in patterns.items():
                if pattern in content:
                    suggestions.append(
                        {
                            "file": str(path),
                            "issue": f"Uses {pattern}",
                            "recommendation": recommendation,
                        }
                    )
        return suggestions
