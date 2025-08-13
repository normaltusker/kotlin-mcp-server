import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from utils.security import SecurityManager


@patch.object(SecurityManager, "_setup_audit_database")
@patch.object(SecurityManager, "_setup_security_logging")
def test_validate_file_path_valid(mock_log, mock_db):
    sm = SecurityManager()
    sm.log_audit_event = MagicMock()
    base = Path("/base")
    result = sm.validate_file_path("sub/file.txt", base)
    assert result == (base / "sub" / "file.txt").resolve()
    sm.log_audit_event.assert_not_called()


@patch.object(SecurityManager, "_setup_audit_database")
@patch.object(SecurityManager, "_setup_security_logging")
def test_validate_file_path_traversal(mock_log, mock_db):
    sm = SecurityManager()
    base = Path("/base")
    with pytest.raises(ValueError):
        sm.validate_file_path("../secret.txt", base)


@patch.object(SecurityManager, "_setup_audit_database")
@patch.object(SecurityManager, "_setup_security_logging")
def test_validate_file_path_hidden_logs(mock_log, mock_db):
    sm = SecurityManager()
    sm.log_audit_event = MagicMock()
    base = Path("/base")
    sm.validate_file_path(".hidden/file.txt", base)
    sm.log_audit_event.assert_called_with("file_access", "hidden_file:.hidden")

@patch.object(SecurityManager, "_setup_audit_database")
@patch.object(SecurityManager, "_setup_security_logging")
def test_validate_file_path_absolute(mock_log, mock_db, tmp_path):
    sm = SecurityManager()
    result = sm.validate_file_path(str(tmp_path / "file.txt"), tmp_path)
    assert result == (tmp_path / "file.txt").resolve()


@patch.object(SecurityManager, "_setup_audit_database")
@patch.object(SecurityManager, "_setup_security_logging")
def test_validate_file_path_os_error(mock_log, mock_db):
    sm = SecurityManager()
    base = Path("/base")
    with patch("pathlib.Path.resolve", side_effect=OSError("fail")):
        with pytest.raises(ValueError):
            sm.validate_file_path("file.txt", base)


@patch.object(SecurityManager, "_setup_audit_database")
@patch.object(SecurityManager, "_setup_security_logging")
def test_validate_command_args_non_list(mock_log, mock_db):
    sm = SecurityManager()
    with pytest.raises(ValueError):
        sm.validate_command_args("rm")


@patch.object(SecurityManager, "_setup_audit_database")
@patch.object(SecurityManager, "_setup_security_logging")
def test_validate_command_args_non_str_items(mock_log, mock_db):
    sm = SecurityManager()
    assert sm.validate_command_args(["echo", 123]) == ["echo", "123"]


@patch.object(SecurityManager, "_setup_audit_database")
@patch.object(SecurityManager, "_setup_security_logging")
def test_validate_command_args_dangerous(mock_log, mock_db):
    sm = SecurityManager()
    sm.log_audit_event = MagicMock()
    with pytest.raises(ValueError):
        sm.validate_command_args(["safe", "rm -rf /"])
    sm.log_audit_event.assert_called_with(
        "security_violation", "dangerous_command_arg:rm -rf /"
    )


@patch.object(SecurityManager, "_setup_audit_database")
@patch.object(SecurityManager, "_setup_security_logging")
def test_close_closes_db(mock_log, mock_db):
    sm = SecurityManager()
    sm.audit_db = MagicMock()
    sm.close()
    sm.audit_db.close.assert_called_once()


@patch("utils.security.sqlite3.connect", return_value=MagicMock())
@patch("utils.security.logging.FileHandler", side_effect=PermissionError("denied"))
def test_setup_security_logging_failure(mock_filehandler, mock_connect):
    sm = SecurityManager()
    assert sm.security_logger is None


@patch("utils.security.logging.FileHandler")
@patch("utils.security.sqlite3.connect", side_effect=OSError("db error"))
def test_setup_audit_database_failure(mock_connect, mock_filehandler):
    sm = SecurityManager()
    assert sm.audit_db is None
