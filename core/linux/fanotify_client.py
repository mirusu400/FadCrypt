"""
Fanotify Client - Connects to daemon's fanotify permission socket

Receives permission requests from the daemon and responds with allow/deny
based on user's password input.
"""

import socket
import json
import threading
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

FANOTIFY_SOCKET = "/run/fadcrypt/fanotify.sock"


class FanotifyClient:
    """
    Client that connects to daemon's fanotify permission socket.
    
    When a file access is detected by the daemon, it sends a permission
    request to this client. The client shows a password dialog and responds
    with allow/deny.
    """
    
    def __init__(self, password_callback: Callable[[str, int], bool]):
        """
        Initialize fanotify client.
        
        Args:
            password_callback: Function to call for password verification
                              Signature: callback(file_path, pid) -> bool
                              Returns True if access should be allowed
        """
        self.password_callback = password_callback
        self.running = False
        self.client_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start listening for permission requests"""
        if self.running:
            logger.warning("Fanotify client already running")
            return
        
        self.running = True
        self.client_thread = threading.Thread(target=self._client_loop, daemon=True)
        self.client_thread.start()
        logger.info("Fanotify client started")
    
    def stop(self):
        """Stop listening for permission requests"""
        self.running = False
        if self.client_thread:
            self.client_thread.join(timeout=2.0)
            self.client_thread = None
        logger.info("Fanotify client stopped")
    
    def _client_loop(self):
        """Main client loop - connects to daemon and handles requests"""
        logger.info("Fanotify client loop started")
        
        while self.running:
            try:
                # Connect to daemon's permission socket
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(1.0)  # Short timeout for checking self.running
                
                try:
                    sock.connect(FANOTIFY_SOCKET)
                except (socket.error, FileNotFoundError):
                    # Socket not available yet, retry
                    sock.close()
                    continue
                
                # Receive permission request
                try:
                    data = sock.recv(4096).decode().strip()
                    
                    if not data:
                        sock.close()
                        continue
                    
                    request = json.loads(data)
                    
                    if request.get("type") != "permission_request":
                        sock.close()
                        continue
                    
                    path = request.get("path")
                    pid = request.get("pid")
                    
                    logger.info(f"Permission request: {path} (PID: {pid})")
                    
                    # Ask user for permission (this will show password dialog)
                    allowed = self.password_callback(path, pid)
                    
                    # Send response
                    response = {"allowed": allowed}
                    sock.sendall(json.dumps(response).encode() + b'\n')
                    
                    logger.info(f"Response: {'ALLOWED' if allowed else 'DENIED'}")
                    
                except socket.timeout:
                    pass  # Normal timeout, continue loop
                except Exception as e:
                    logger.error(f"Error handling request: {e}")
                finally:
                    sock.close()
                    
            except Exception as e:
                if self.running:
                    logger.error(f"Error in client loop: {e}")
        
        logger.info("Fanotify client loop stopped")


# Global client instance
_fanotify_client: Optional[FanotifyClient] = None


def get_fanotify_client(password_callback: Callable[[str, int], bool]) -> FanotifyClient:
    """
    Get or create global fanotify client instance.
    
    Args:
        password_callback: Function to call for password verification
        
    Returns:
        FanotifyClient instance
    """
    global _fanotify_client
    if _fanotify_client is None:
        _fanotify_client = FanotifyClient(password_callback)
    return _fanotify_client
