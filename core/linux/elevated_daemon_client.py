"""
Client interface for FadCrypt Elevated Daemon

Provides methods to communicate with the elevated daemon via Unix socket.
Enables unprivileged user code to perform privileged operations without
prompting for password or polkit authorization.

Usage:
    from core.linux.elevated_daemon_client import ElevatedClient
    
    client = ElevatedClient()
    success, msg = client.chattr(files=['/path/to/file'], set_immutable=True)
"""

import socket
import json
import logging
import os
from typing import Tuple, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Socket location must match daemon
SOCKET_FILE = "/run/fadcrypt/elevated.sock"
SOCKET_TIMEOUT = 10  # seconds


class ElevatedClientError(Exception):
    """Raised when daemon communication fails."""
    pass


class ElevatedClient:
    """Client for communicating with elevated daemon."""
    
    def __init__(self, socket_path: str = SOCKET_FILE):
        """
        Initialize client.
        
        Args:
            socket_path: Path to daemon socket file
        """
        self.socket_path = socket_path
    
    def is_available(self) -> bool:
        """
        Check if daemon is running and available.
        
        Returns:
            True if daemon responds to ping, False otherwise
        """
        try:
            response = self._send_request({'command': 'ping'})
            return response.get('success', False)
        except Exception as e:
            logger.debug(f"Daemon not available: {e}")
            return False
    
    def chattr(self, files: List[str], set_immutable: bool = True) -> Tuple[bool, str]:
        """
        Set or unset immutable flag on files via daemon.
        
        Args:
            files: List of file paths
            set_immutable: True to set +i, False to unset -i
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        mode = '+i' if set_immutable else '-i'
        
        request = {
            'command': 'chattr',
            'mode': mode,
            'files': files
        }
        
        try:
            response = self._send_request(request)
            
            if response.get('success'):
                logger.info(f"Daemon: chattr {mode} on {len(files)} files")
                return True, response.get('message', 'Success')
            else:
                error = response.get('error', 'Unknown error')
                logger.error(f"Daemon chattr failed: {error}")
                return False, error
                
        except Exception as e:
            logger.error(f"Daemon communication failed: {e}")
            return False, f"Daemon error: {e}"
    
    def chmod(self, files: List[str], mode: int = 0o600) -> Tuple[bool, str]:
        """
        Change file permissions via daemon.
        
        Args:
            files: List of file paths
            mode: Octal permission mode (e.g., 0o600)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        request = {
            'command': 'chmod',
            'mode': mode,
            'files': files
        }
        
        try:
            response = self._send_request(request)
            
            if response.get('success'):
                logger.info(f"Daemon: chmod {oct(mode)} on {len(files)} files")
                return True, response.get('message', 'Success')
            else:
                error = response.get('error', 'Unknown error')
                logger.error(f"Daemon chmod failed: {error}")
                return False, error
                
        except Exception as e:
            logger.error(f"Daemon communication failed: {e}")
            return False, f"Daemon error: {e}"
    
    def _send_request(self, request: dict) -> dict:
        """
        Send request to daemon and receive response.
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary from daemon
            
        Raises:
            ElevatedClientError: If communication fails
        """
        # Check if socket exists
        if not os.path.exists(self.socket_path):
            raise ElevatedClientError(
                f"Daemon socket not found at {self.socket_path}. "
                "Is fadcrypt-elevated.service running?"
            )
        
        try:
            # Connect to daemon
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_TIMEOUT)
            sock.connect(self.socket_path)
            
            # Send request
            request_json = json.dumps(request)
            sock.send(request_json.encode())
            
            # Receive response
            response_data = sock.recv(8192)
            sock.close()
            
            if not response_data:
                raise ElevatedClientError("Daemon returned empty response")
            
            response = json.loads(response_data.decode())
            logger.debug(f"Daemon response: {response}")
            
            return response
            
        except socket.timeout:
            raise ElevatedClientError("Daemon request timeout")
        except socket.error as e:
            raise ElevatedClientError(f"Socket error: {e}")
        except json.JSONDecodeError as e:
            raise ElevatedClientError(f"Invalid response from daemon: {e}")
        except Exception as e:
            raise ElevatedClientError(f"Unexpected error: {e}")


# Global client instance
_client = None


def get_elevated_client() -> ElevatedClient:
    """
    Get or create global elevated client instance.
    
    Returns:
        ElevatedClient instance
    """
    global _client
    if _client is None:
        _client = ElevatedClient()
    return _client
