"""
File Access Monitor - Monitors file/folder access attempts and prompts for password

This module provides real-time monitoring of locked files/folders using the watchdog library.
When a user attempts to access a locked file, it shows a password dialog.

Cross-platform support for Linux and Windows.
"""

import os
import time
import threading
from typing import Callable, Optional, List, Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class FileAccessHandler(FileSystemEventHandler):
    """Handler for file system events on monitored files/folders"""
    
    def __init__(self, locked_paths: List[str], on_access_callback: Callable):
        """
        Initialize the file access handler
        
        Args:
            locked_paths: List of file/folder paths that are locked
            on_access_callback: Function to call when locked file is accessed
                                Signature: callback(file_path) -> bool (True if access allowed)
        """
        super().__init__()
        self.locked_paths = set(os.path.abspath(p) for p in locked_paths)
        self.on_access_callback = on_access_callback
        self.last_event_time = {}  # Debounce events
        self.debounce_seconds = 5.0  # Ignore events within 5 seconds (increased to reduce spam)
        self.start_time = time.time()  # Track when monitoring started
        self.initial_grace_period = 3.0  # Ignore events for first 3 seconds after start
        
    def _should_process_event(self, path: str) -> bool:
        """Check if we should process this event (debouncing + grace period)"""
        now = time.time()
        
        # Ignore events during initial grace period (prevents spurious events on startup)
        if now - self.start_time < self.initial_grace_period:
            return False
        
        last_time = self.last_event_time.get(path, 0)
        
        if now - last_time < self.debounce_seconds:
            return False
        
        self.last_event_time[path] = now
        return True
    
    def _get_process_info(self, file_path: str) -> tuple:
        """
        Get information about process accessing the file
        
        Returns:
            tuple: (process_info_string, pid) or ("", None) if not found
        """
        try:
            import psutil
            import subprocess
            
            # Try lsof first
            try:
                result = subprocess.run(
                    ['lsof', file_path],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        # Parse lsof output (PID is usually in column 2)
                        parts = lines[1].split()
                        if len(parts) >= 2:
                            pid = int(parts[1])
                            proc = psutil.Process(pid)
                            info = f" [Process: {proc.name()} (PID: {pid})]"
                            return (info, pid)
            except (subprocess.SubprocessError, ValueError, psutil.NoSuchProcess):
                pass
            
            # Fallback: Use ps aux | grep
            # This is more reliable for detecting editors that have files open
            try:
                filename = os.path.basename(file_path)
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0:
                    # Look for lines containing the full file path
                    for line in result.stdout.split('\n'):
                        if file_path in line and 'grep' not in line and 'ps aux' not in line:
                            # Parse ps output to get PID (second column)
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    pid = int(parts[1])
                                    # Extract command name (11th column onward)
                                    cmd = ' '.join(parts[10:])
                                    # Get just the command name
                                    cmd_name = os.path.basename(parts[10])
                                    info = f" [Process: {cmd_name} (PID: {pid})]"
                                    return (info, pid)
                                except (ValueError, IndexError):
                                    pass
            except subprocess.SubprocessError:
                pass
            
            return ("", None)
        except Exception:
            return ("", None)
    
    def _kill_process_accessing_file(self, file_path: str) -> bool:
        """
        Kill process(es) accessing the locked file with robust approach
        (Based on unified_monitor.py _block_processes method)
        
        Returns:
            bool: True if process was killed, False otherwise
        """
        try:
            import psutil
            import subprocess
            
            pids_to_kill = []
            
            # Method 1: Try lsof
            try:
                result = subprocess.run(
                    ['lsof', '-t', file_path],  # -t returns only PIDs
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0 and result.stdout:
                    pids_to_kill.extend([int(pid.strip()) for pid in result.stdout.strip().split('\n') if pid.strip()])
            except subprocess.SubprocessError:
                pass
            
            # Method 2: Use ps aux | grep (more reliable for editors)
            if not pids_to_kill:
                try:
                    result = subprocess.run(
                        ['ps', 'aux'],
                        capture_output=True,
                        text=True,
                        timeout=1
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if file_path in line and 'grep' not in line and 'ps aux' not in line:
                                parts = line.split()
                                if len(parts) >= 2:
                                    try:
                                        pid = int(parts[1])
                                        if pid not in pids_to_kill:
                                            pids_to_kill.append(pid)
                                    except ValueError:
                                        pass
                except subprocess.SubprocessError:
                    pass
            
            # Kill all found processes with robust approach
            killed_any = False
            for pid in pids_to_kill:
                try:
                    proc = psutil.Process(pid)
                    
                    # Skip zombie processes (they can't be killed anyway)
                    if proc.status() == psutil.STATUS_ZOMBIE:
                        print(f"   [SKIP] Process {pid} is zombie - skipping")
                        continue
                    
                    proc_name = proc.name()
                    
                    # Kill direct children first (non-recursive for performance)
                    for child in proc.children(recursive=False):
                        try:
                            print(f"   [KILL] Terminating child process: {child.name()} (PID: {child.pid})")
                            child.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                            print(f"   [SKIP] Could not kill child {child.pid}: {e}")
                            pass
                    
                    print(f"⚔️  Killing process accessing locked file: {proc_name} (PID: {pid})")
                    proc.kill()  # Use kill() instead of terminate() for immediate termination
                    killed_any = True
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"⚠️  Could not kill process {pid}: {e}")
            
            return killed_any
        except Exception as e:
            print(f"⚠️  Error killing process: {e}")
            return False
    
    def _is_locked_path(self, path: str) -> bool:
        """Check if the path is a locked file or inside a locked folder"""
        abs_path = os.path.abspath(path)
        
        # Exact match
        if abs_path in self.locked_paths:
            return True
        
        # Check if path is inside a locked folder
        for locked_path in self.locked_paths:
            if abs_path.startswith(locked_path + os.sep):
                return True
        
        return False
    
    def _get_locked_parent_folder(self, file_path: str) -> Optional[str]:
        """Get the locked folder that contains this file (if any)"""
        abs_path = os.path.abspath(file_path)
        
        for locked_path in self.locked_paths:
            if abs_path.startswith(locked_path + os.sep):
                return locked_path
        
        return None
    
    def on_modified(self, event: FileSystemEvent):
        """Called when a file is modified"""
        if not event.is_directory and self._is_locked_path(event.src_path):
            if self._should_process_event(event.src_path):
                # CRITICAL: Only proceed if we detect a process accessing the file
                proc_info, pid = self._get_process_info(event.src_path)
                
                # If no process detected, ignore this event (likely internal filesystem activity)
                if not pid:
                    return
                
                # Check if file is inside a locked folder
                locked_folder = self._get_locked_parent_folder(event.src_path)
                if locked_folder:
                    # File is inside a locked folder - show dialog for folder, not file
                    if self._should_process_event(locked_folder):
                        print(f"🔒 Locked folder access detected: {locked_folder}{proc_info}")
                        unlocked = self.on_access_callback(locked_folder)
                        
                        # Only kill process if user FAILED to unlock (wrong password or cancel)
                        if not unlocked:
                            self._kill_process_accessing_file(event.src_path)
                else:
                    # File is directly locked
                    print(f"🔒 Locked file access detected: {event.src_path}{proc_info}")
                    unlocked = self.on_access_callback(event.src_path)
                    
                    # Only kill process if user FAILED to unlock (wrong password or cancel)
                    if not unlocked:
                        self._kill_process_accessing_file(event.src_path)
    
    def on_created(self, event: FileSystemEvent):
        """Called when a file is created (might indicate attempted access)"""
        if not event.is_directory and self._is_locked_path(event.src_path):
            if self._should_process_event(event.src_path):
                # CRITICAL: Only proceed if we detect a process accessing the file
                proc_info, pid = self._get_process_info(event.src_path)
                
                # If no process detected, ignore this event
                if not pid:
                    return
                
                # Check if file is inside a locked folder
                locked_folder = self._get_locked_parent_folder(event.src_path)
                if locked_folder:
                    if self._should_process_event(locked_folder):
                        print(f"🔒 Locked folder access detected (creation): {locked_folder}{proc_info}")
                        unlocked = self.on_access_callback(locked_folder)
                        
                        # Only kill process if user FAILED to unlock
                        if not unlocked:
                            self._kill_process_accessing_file(event.src_path)
                else:
                    print(f"🔒 Locked file access detected (creation): {event.src_path}{proc_info}")
                    unlocked = self.on_access_callback(event.src_path)
                    
                    # Only kill process if user FAILED to unlock
                    if not unlocked:
                        self._kill_process_accessing_file(event.src_path)
    
    def on_opened(self, event: FileSystemEvent):
        """Called when a file is opened (if supported by platform)"""
        if not event.is_directory and self._is_locked_path(event.src_path):
            if self._should_process_event(event.src_path):
                # CRITICAL: Only proceed if we detect a process accessing the file
                proc_info, pid = self._get_process_info(event.src_path)
                
                # If no process detected, ignore this event
                if not pid:
                    return
                
                # Check if file is inside a locked folder
                locked_folder = self._get_locked_parent_folder(event.src_path)
                if locked_folder:
                    if self._should_process_event(locked_folder):
                        print(f"🔒 Locked folder file open: {locked_folder}{proc_info}")
                        unlocked = self.on_access_callback(locked_folder)
                        
                        # Only kill process if user FAILED to unlock
                        if not unlocked:
                            self._kill_process_accessing_file(event.src_path)
                else:
                    print(f"🔒 Locked file open detected: {event.src_path}{proc_info}")
                    unlocked = self.on_access_callback(event.src_path)
                    
                    # Only kill process if user FAILED to unlock
                    if not unlocked:
                        self._kill_process_accessing_file(event.src_path)


class FileAccessMonitor:
    """
    Monitors locked files/folders for access attempts and triggers password dialogs.
    
    This is similar to UnifiedMonitor but for file system access instead of process monitoring.
    Includes auto-lock functionality that re-locks files when no longer in use.
    """
    
    def __init__(self, file_lock_manager, password_callback: Callable, get_state_func: Callable = None, set_state_func: Callable = None):
        """
        Initialize the file access monitor
        
        Args:
            file_lock_manager: The FileLockManager instance
            password_callback: Function to call for password verification
                              Signature: callback(file_path) -> bool (True if access granted)
            get_state_func: Function to get monitoring state (returns dict with 'unlocked_files')
            set_state_func: Function to update monitoring state
        """
        self.file_lock_manager = file_lock_manager
        self.password_callback = password_callback
        self.get_state = get_state_func if get_state_func else lambda: {}
        self.set_state = set_state_func if set_state_func else lambda key, value: None
        self.observer = None
        self.event_handler = None
        self.is_monitoring = False
        self.monitored_paths = []
        self.auto_lock_thread = None
        self.auto_lock_running = False
        
        # Track consecutive checks with no processes (for auto-lock)
        self.no_process_counts = {}  # {file_path: count}
        
    def start_monitoring(self):
        """Start monitoring locked files/folders for access attempts"""
        if self.is_monitoring:
            print("⚠️  File monitoring already active")
            return False
        
        # Get list of locked items
        locked_items = self.file_lock_manager.locked_items
        if not locked_items:
            print("ℹ️  No locked items to monitor")
            return False
        
        # Extract paths and parent directories to watch
        self.monitored_paths = []
        watch_dirs = set()
        
        for item in locked_items:
            path = item['path']
            self.monitored_paths.append(path)
            
            # Watch parent directory for file events
            parent_dir = os.path.dirname(path)
            if os.path.exists(parent_dir):
                watch_dirs.add(parent_dir)
            
            # If it's a folder, also watch it directly
            if item['type'] == 'folder' and os.path.exists(path):
                watch_dirs.add(path)
        
        # Create event handler
        self.event_handler = FileAccessHandler(
            locked_paths=self.monitored_paths,
            on_access_callback=self._handle_file_access
        )
        
        # Create and start observer
        self.observer = Observer()
        
        for watch_dir in watch_dirs:
            try:
                self.observer.schedule(
                    self.event_handler,
                    watch_dir,
                    recursive=True
                )
                print(f"👁️  Watching: {watch_dir}")
            except Exception as e:
                print(f"⚠️  Could not watch {watch_dir}: {e}")
        
        self.observer.start()
        self.is_monitoring = True
        
        # Start auto-lock thread
        self.auto_lock_running = True
        self.auto_lock_thread = threading.Thread(target=self._auto_lock_loop, daemon=True)
        self.auto_lock_thread.start()
        
        print(f"✅ File access monitoring started for {len(self.monitored_paths)} items")
        return True
    
    def _auto_lock_loop(self):
        """
        Background thread that checks unlocked files and re-locks them when not in use
        Similar to unified_monitor's auto-lock logic
        """
        import subprocess
        
        while self.auto_lock_running:
            try:
                time.sleep(2)  # Check every 2 seconds
                
                state = self.get_state()
                unlocked_files = state.get('unlocked_files', [])
                
                if not unlocked_files:
                    continue
                
                files_to_relock = []
                
                for file_path in unlocked_files:
                    # Check if any process is using this file
                    has_process = False
                    
                    try:
                        # Method 1: Try lsof
                        result = subprocess.run(
                            ['lsof', file_path],
                            capture_output=True,
                            text=True,
                            timeout=0.5
                        )
                        if result.returncode == 0 and result.stdout:
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 1:  # Header + at least one process
                                has_process = True
                    except:
                        pass
                    
                    # Method 2: ps aux fallback
                    if not has_process:
                        try:
                            result = subprocess.run(
                                ['ps', 'aux'],
                                capture_output=True,
                                text=True,
                                timeout=0.5
                            )
                            if result.returncode == 0:
                                for line in result.stdout.split('\n'):
                                    if file_path in line and 'grep' not in line and 'ps aux' not in line:
                                        has_process = True
                                        break
                        except:
                            pass
                    
                    # Update no-process counter
                    if not has_process:
                        self.no_process_counts[file_path] = self.no_process_counts.get(file_path, 0) + 1
                        
                        # Auto-lock after 5 consecutive checks (10 seconds)
                        if self.no_process_counts[file_path] >= 5:
                            files_to_relock.append(file_path)
                    else:
                        # Reset counter if process found
                        self.no_process_counts[file_path] = 0
                
                # Re-lock files that have been idle
                for file_path in files_to_relock:
                    try:
                        import stat
                        original_stat = os.stat(file_path)
                        is_dir = stat.S_ISDIR(original_stat.st_mode)
                        
                        # Re-lock
                        if is_dir:
                            os.chmod(file_path, 0o555)  # r-xr-xr-x
                        else:
                            os.chmod(file_path, 0o444)  # r--r--r--
                        
                        filename = os.path.basename(file_path)
                        print(f"🔒 [AUTO-LOCK] Re-locked {filename} (no active processes)")
                        
                        # Remove from unlocked state
                        unlocked_files.remove(file_path)
                        self.set_state('unlocked_files', unlocked_files)
                        
                        # Reset counter
                        self.no_process_counts[file_path] = 0
                        
                    except Exception as e:
                        print(f"⚠️  [AUTO-LOCK] Could not re-lock {os.path.basename(file_path)}: {e}")
                
            except Exception as e:
                print(f"⚠️  [AUTO-LOCK] Error in auto-lock loop: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring file access"""
        if not self.is_monitoring:
            return False
        
        # Stop auto-lock thread
        self.auto_lock_running = False
        if self.auto_lock_thread:
            self.auto_lock_thread.join(timeout=3)
            self.auto_lock_thread = None
        
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.observer = None
        
        self.event_handler = None
        self.monitored_paths = []
        self.is_monitoring = False
        print("🛑 File access monitoring stopped")
        return True
    
    def _handle_file_access(self, file_path: str):
        """
        Handle detected file access attempt
        
        Args:
            file_path: Path to the file that was accessed
        """
        print(f"🚨 Access attempt detected: {os.path.basename(file_path)}")
        
        # Call password callback (will show dialog in UI thread)
        try:
            access_granted = self.password_callback(file_path)
            
            if access_granted:
                print(f"✅ Access granted to: {os.path.basename(file_path)}")
                # Temporarily unlock the file (UI will handle this)
            else:
                print(f"❌ Access denied to: {os.path.basename(file_path)}")
                # Keep file locked
        except Exception as e:
            print(f"❌ Error handling file access: {e}")
    
    def update_monitored_items(self):
        """Update the list of monitored items (called when items are added/removed)"""
        if self.is_monitoring:
            # Restart monitoring with updated list
            self.stop_monitoring()
            self.start_monitoring()
