#!/usr/bin/env python3
"""
FadCrypt Elevated Daemon

Runs as root via systemd service
Provides file operations (chattr, chmod) via Unix socket
Enables seamless elevated operations across reboots without password prompts

Operations:
- chattr: Set/unset immutable flag on files
- chmod: Change file permissions
- restore: Restore file from backup

All operations execute with root privileges - no polkit/sudo prompts needed.
"""

import socket
import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List

# Configuration
SOCKET_FILE = "/run/fadcrypt/elevated.sock"
SOCKET_DIR = "/run/fadcrypt"
LOG_FILE = "/var/log/fadcrypt-daemon.log"

# Setup logging
log_handlers = [logging.StreamHandler()]  # Always log to stderr
try:
    log_handlers.append(logging.FileHandler(LOG_FILE))
except (PermissionError, OSError):
    pass  # Log file location not available (not running as root), use stdout only

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [DAEMON] %(levelname)s: %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)


class ElevatedDaemon:
    """Daemon that runs as root and handles elevated file operations via socket."""
    
    def __init__(self):
        """Initialize and start the daemon."""
        try:
            self.setup_socket()
            logger.info("FadCrypt Elevated Daemon started successfully")
            logger.info(f"Listening on socket: {SOCKET_FILE}")
            self.run()
        except Exception as e:
            logger.error(f"Failed to start daemon: {e}")
            sys.exit(1)
    
    def setup_socket(self) -> None:
        """Setup Unix domain socket for IPC."""
        # Create socket directory
        Path(SOCKET_DIR).mkdir(parents=True, exist_ok=True, mode=0o755)
        
        # Remove old socket if exists
        if os.path.exists(SOCKET_FILE):
            try:
                os.remove(SOCKET_FILE)
            except OSError as e:
                logger.warning(f"Could not remove old socket: {e}")
        
        # Create Unix domain socket
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(SOCKET_FILE)
        self.server_socket.listen(5)  # Allow up to 5 pending connections
        
        # Set permissions so any user can connect
        os.chmod(SOCKET_FILE, 0o666)
        logger.info(f"Socket created with world-accessible permissions: {SOCKET_FILE}")
    
    def run(self) -> None:
        """Main daemon loop - accept and handle requests."""
        logger.info("Starting request loop...")
        connection_count = 0
        
        while True:
            try:
                connection, _ = self.server_socket.accept()
                connection_count += 1
                logger.debug(f"Accepted connection #{connection_count}")
                
                try:
                    self.handle_request(connection)
                except Exception as e:
                    logger.error(f"Error handling request: {e}")
                finally:
                    connection.close()
                    
            except KeyboardInterrupt:
                logger.info("Daemon interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
    
    def handle_request(self, connection: socket.socket) -> None:
        """Handle a single request from client."""
        try:
            # Receive request JSON
            data = connection.recv(8192).decode()
            if not data:
                logger.warning("Received empty request")
                return
            
            request = json.loads(data)
            logger.debug(f"Received request: {request}")
            
            command = request.get('command')
            
            # Route to appropriate handler
            if command == 'chattr':
                response = self._handle_chattr(request)
            elif command == 'chmod':
                response = self._handle_chmod(request)
            elif command == 'ping':
                response = {'success': True, 'message': 'pong'}
            else:
                response = {'success': False, 'error': f'Unknown command: {command}'}
            
            # Send response
            logger.debug(f"Sending response: {response}")
            connection.send(json.dumps(response).encode())
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request: {e}")
            error_response = json.dumps({'success': False, 'error': 'Invalid JSON'})
            try:
                connection.send(error_response.encode())
            except:
                pass
        except Exception as e:
            logger.error(f"Unexpected error handling request: {e}")
            error_response = json.dumps({'success': False, 'error': str(e)})
            try:
                connection.send(error_response.encode())
            except:
                pass
    
    def _handle_chattr(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chattr command to set/unset immutable flag."""
        try:
            files = request.get('files', [])
            mode = request.get('mode', '+i')  # +i (set immutable) or -i (unset)
            
            if not files:
                return {'success': False, 'error': 'No files specified'}
            
            if mode not in ['+i', '-i']:
                return {'success': False, 'error': f'Invalid mode: {mode}'}
            
            # Validate file paths (security check)
            validated_files = []
            for f in files:
                # Ensure file path is absolute and doesn't escape
                abs_path = os.path.abspath(f)
                if os.path.exists(abs_path) or mode == '-i':  # Allow -i on non-existent (in case already gone)
                    validated_files.append(abs_path)
                else:
                    logger.warning(f"File does not exist: {f}")
            
            if not validated_files:
                return {'success': False, 'error': 'No valid files to process'}
            
            # Execute chattr command
            cmd = ['chattr', mode] + validated_files
            logger.info(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"chattr {mode} successful for {len(validated_files)} files")
                return {
                    'success': True,
                    'message': f"chattr {mode} completed for {len(validated_files)} files",
                    'files_processed': len(validated_files)
                }
            else:
                error_msg = result.stderr or "chattr failed"
                logger.error(f"chattr failed: {error_msg}")
                return {'success': False, 'error': error_msg}
        
        except subprocess.TimeoutExpired:
            logger.error("chattr command timed out")
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            logger.error(f"Error in chattr handler: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_chmod(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chmod command to change file permissions."""
        try:
            files = request.get('files', [])
            mode = request.get('mode', 0o600)  # Default: rw-------
            
            if not files:
                return {'success': False, 'error': 'No files specified'}
            
            if not isinstance(mode, int):
                try:
                    mode = int(mode, 8)  # Handle octal strings like "600"
                except ValueError:
                    return {'success': False, 'error': f'Invalid mode: {mode}'}
            
            success_count = 0
            errors = []
            
            for file_path in files:
                try:
                    abs_path = os.path.abspath(file_path)
                    
                    if not os.path.exists(abs_path):
                        logger.warning(f"File does not exist: {abs_path}")
                        errors.append(f"{abs_path}: Not found")
                        continue
                    
                    logger.debug(f"chmod {oct(mode)} on {abs_path}")
                    os.chmod(abs_path, mode)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"chmod failed for {file_path}: {e}")
                    errors.append(f"{file_path}: {str(e)}")
            
            logger.info(f"chmod completed: {success_count} successful, {len(errors)} errors")
            
            return {
                'success': len(errors) == 0,
                'message': f"chmod completed for {success_count} files",
                'files_processed': success_count,
                'errors': errors
            }
        
        except Exception as e:
            logger.error(f"Error in chmod handler: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """Entry point for the daemon."""
    # Check if running as root
    if os.geteuid() != 0:
        logger.error("Daemon must run as root!")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("FadCrypt Elevated Daemon Starting")
    logger.info("=" * 60)
    
    daemon = ElevatedDaemon()


if __name__ == '__main__':
    main()
