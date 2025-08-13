#!/usr/bin/env python3
"""
Test Suite for Utils Security Module
Tests security utilities and encryption functionality
"""

import tempfile

import pytest
from cryptography.fernet import Fernet

from kotlin_mcp_server import KotlinMCPServer
from utils.security import check_password, decrypt_data, encrypt_data, hash_password


class TestSecurityUtils:
    """Test suite for security utilities functionality"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServer":
        """Create server instance for testing"""
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    def test_encrypt_decrypt(self) -> None:
        """Test data encryption and decryption"""
        key = Fernet.generate_key()
        data = b"test data"
        encrypted = encrypt_data(data, key)
        decrypted = decrypt_data(encrypted, key)
        assert data == decrypted

    def test_hash_check_password(self) -> None:
        """Test password hashing and verification"""
        password = "test_password"
        hashed = hash_password(password)
        assert check_password(password, hashed)
        assert not check_password("wrong_password", hashed)

    @pytest.mark.asyncio
    async def test_encrypt_sensitive_data(self, server: KotlinMCPServer) -> None:
        """Test sensitive data encryption tool"""
        result = await server.handle_call_tool(
            "encrypt_sensitive_data", {"data_type": "personal_info", "encryption_method": "AES256"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_setup_secure_storage(self, server: KotlinMCPServer) -> None:
        """Test secure storage setup"""
        result = await server.handle_call_tool(
            "setup_secure_storage",
            {"storage_type": "encrypted_sharedprefs", "encryption_level": "AES256"},
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_setup_cloud_sync(self, server: KotlinMCPServer) -> None:
        """Test cloud sync setup"""
        result = await server.handle_call_tool(
            "setup_cloud_sync", {"provider": "firebase", "sync_type": "realtime"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_security_tools_variations(self, server: KotlinMCPServer) -> None:
        """Test security tools with various configurations"""
        test_cases = [
            ("encrypt_sensitive_data", {"data_type": "financial", "encryption_method": "RSA"}),
            ("setup_secure_storage", {"storage_type": "keystore", "encryption_level": "AES128"}),
            ("setup_cloud_sync", {"provider": "aws", "sync_type": "batch"}),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result
            assert isinstance(result["content"], list)

    def test_encryption_with_different_keys(self) -> None:
        """Test encryption with different keys"""
        key1 = Fernet.generate_key()
        key2 = Fernet.generate_key()
        data = b"sensitive data"

        encrypted_with_key1 = encrypt_data(data, key1)

        # Should decrypt correctly with the same key
        decrypted = decrypt_data(encrypted_with_key1, key1)
        assert data == decrypted

        # Should fail with different key
        with pytest.raises(Exception):
            decrypt_data(encrypted_with_key1, key2)

    def test_password_hash_uniqueness(self) -> None:
        """Test that password hashes are unique"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify correctly
        assert check_password(password, hash1)
        assert check_password(password, hash2)

    @pytest.mark.asyncio
    async def test_security_edge_cases(self, server: KotlinMCPServer) -> None:
        """Test security tools with edge cases"""
        # Test with empty data type
        result = await server.handle_call_tool(
            "encrypt_sensitive_data", {"data_type": "", "encryption_method": "AES256"}
        )
        assert "content" in result

        # Test with invalid provider
        result = await server.handle_call_tool(
            "setup_cloud_sync", {"provider": "invalid_provider", "sync_type": "realtime"}
        )
        assert "content" in result
