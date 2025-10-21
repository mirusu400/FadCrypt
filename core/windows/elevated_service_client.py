"""
Windows Elevated Service Client

Communicates with FadCrypt Windows Service via named pipes.
Service runs as SYSTEM - no UAC/password prompts needed.

The service is registered as a Windows Service and auto-starts with the system.
All file operations execute with system privileges silently.
"""

import json
import logging
from typing import Tuple, List
import os

logger = logging.getLogger(__name__)

# Named pipe configuration (must match service)
PIPE_NAME = r'\\.\pipe\FadCryptElevated'


class ElevatedServiceError(Exception):
    """Raised when service communication fails."""
    pass


class WindowsElevatedClient:
    """Client for communicating with Windows Elevated Service."""
    
    def __init__(self, pipe_name: str = PIPE_NAME):
        """
        Initialize client.
        
        Args:
            pipe_name: Named pipe name for service communication
        """
        self.pipe_name = pipe_name
    
    def is_available(self) -> bool:
        """
        Check if service is running.
        
        Returns:
            True if service responds to ping, False otherwise
        """
        try:
            response = self._send_request({'command': 'ping'})
            return response.get('success', False)
        except Exception as e:
            logger.debug(f"Service not available: {e}")
            return False
    
    def protect_files(self, files: List[str]) -> Tuple[bool, str]:
        """
        Protect files by setting attributes (Hidden + System + ReadOnly).
        
        Requires service running as SYSTEM - no password prompt needed.
        Works across reboots - service auto-starts at boot.
        
        Args:
            files: List of file paths to protect
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        request = {
            'command': 'protect',
            'files': files
        }
        
        try:
            response = self._send_request(request)
            
            if response.get('success'):
                count = response.get('files_protected', 0)
                logger.info(f"Service: Protected {count} files")
                return True, response.get('message', 'Files protected')
            else:
                error = response.get('error', 'Unknown error')
                logger.error(f"Service protect failed: {error}")
                return False, error
        
        except Exception as e:
            logger.error(f"Service communication failed: {e}")
            return False, f"Service error: {e}"
    
    def unprotect_files(self, files: List[str]) -> Tuple[bool, str]:
        """
        Remove protection from files (remove attributes).
        
        Args:
            files: List of file paths to unprotect
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        request = {
            'command': 'unprotect',
            'files': files
        }
        
        try:
            response = self._send_request(request)
            
            if response.get('success'):
                count = response.get('files_unprotected', 0)
                logger.info(f"Service: Unprotected {count} files")
                return True, response.get('message', 'Files unprotected')
            else:
                error = response.get('error', 'Unknown error')
                logger.error(f"Service unprotect failed: {error}")
                return False, error
        
        except Exception as e:
            logger.error(f"Service communication failed: {e}")
            return False, f"Service error: {e}"
    
    def _send_request(self, request: dict) -> dict:
        """
        Send request to service via named pipe.
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary from service
            
        Raises:
            ElevatedServiceError: If communication fails
        """
        try:
            # Try to open named pipe
            # This requires the Windows API - pywin32 or manual implementation
            
            # For now, return error (actual implementation needs pywin32)
            raise ElevatedServiceError(
                "Named pipe communication not implemented. "
                "Install pywin32 and use win32pipe.CreateFile() / ReadFile() / WriteFile()"
            )
        
        except Exception as e:
            raise ElevatedServiceError(f"Pipe error: {e}")


# Global client instance
_client = None


def get_windows_elevated_client() -> WindowsElevatedClient:
    """
    Get or create global Windows elevated client instance.
    
    Returns:
        WindowsElevatedClient instance
    """
    global _client
    if _client is None:
        _client = WindowsElevatedClient()
    return _client
