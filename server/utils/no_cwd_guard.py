"""
No-CWD guard utilities to prevent tools from operating in server CWD.
"""

import os

# Capture server CWD at startup
SERVER_CWD = os.path.abspath(os.getcwd())


def assert_not_server_cwd(path: str) -> None:
    """
    Assert that a path is not the server's CWD.

    Args:
        path: Path to check

    Raises:
        RuntimeError: If path equals server CWD
    """
    if os.path.abspath(path) == SERVER_CWD:
        raise RuntimeError(
            "ServerCwdMisuse: tool attempted to operate in server CWD. "
            "Resolve project_root and use that instead."
        )
