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
    
    def __init__(self, locked_paths: List[str], on_access_callback: Callable, get_state_func: Callable = None):
        """
        Initialize the file access handler
        
        Args:
            locked_paths: List of file/folder paths that are locked
            on_access_callback: Function to call when locked file is accessed
                                Signature: callback(file_path) -> bool (True if access allowed)
            get_state_func: Function to get monitoring state with unlocked files list
        """
        super().__init__()
        self.locked_paths = set(os.path.abspath(p) for p in locked_paths)
        self.on_access_callback = on_access_callback
        self.get_state = get_state_func if get_state_func else lambda: {}
        self.last_event_time = {}  # Debounce events
        self.debounce_seconds = 0.5  # Shorter debounce for instant detection (was 2.0)

        
    def _should_process_event(self, path: str) -> bool:
        """Check if we should process this event (debouncing only - NO grace period)"""
        now = time.time()
        

        
        last_time = self.last_event_time.get(path, 0)
        
        if now - last_time < self.debounce_seconds:
            return False
        
        self.last_event_time[path] = now
        return True
    
    def _is_file_unlocked(self, file_path: str) -> bool:
        """Check if file is currently unlocked (temporary access granted)"""
        abs_path = os.path.abspath(file_path)
        state = self.get_state()
        unlocked_files = state.get('unlocked_files', [])
        return abs_path in unlocked_files
    
    def _get_process_info(self, file_path: str) -> tuple:
        """
        Get information about process accessing the file
        
        Returns:
            tuple: (process_info_string, pid) or ("", None) if not found
        """
        try:
            import psutil
            import subprocess
            
            # Processes to ignore (monitoring tools, not actual user access)
            IGNORED_PROCESSES = {'lsof', 'ps', 'grep', 'python3', 'python', 'FadCrypt'}
            
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
                            proc_name = proc.name()
                            
                            # Ignore monitoring tools
                            if proc_name in IGNORED_PROCESSES:
                                return ("", None)
                            
                            info = f" [Process: {proc_name} (PID: {pid})]"
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
                                    
                                    # Ignore monitoring tools
                                    if cmd_name in IGNORED_PROCESSES:
                                        continue
                                    
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
    
    def _detect_folder_access(self, folder_path: str) -> tuple:
        """
        Detect if any file manager process is accessing the folder (cross-platform)
        
        Returns:
            tuple: (process_info_string, pid) or ("", None) if not found
        """
        import platform
        system = platform.system()
        
        if system == "Windows":
            return self._detect_folder_access_windows(folder_path)
        else:  # Linux/Unix
            return self._detect_folder_access_linux(folder_path)
    
    def _detect_folder_access_linux(self, folder_path: str) -> tuple:
        """Linux-specific folder access detection"""
        try:
            import psutil
            import subprocess
            
            # COMPREHENSIVE list of Linux file managers and shell commands
            FILE_MANAGERS = {
                # GNOME/GTK file managers
                'nautilus',  # GNOME Files (Ubuntu, Fedora, etc.)
                'nemo',  # Cinnamon Files (Linux Mint)
                'thunar',  # Xfce Files
                'caja',  # MATE Files
                'spacefm',  # SpaceFM
                
                # KDE/Qt file managers  
                'dolphin',  # KDE Plasma Files
                'konqueror',  # KDE Browser/Files
                'krusader',  # KDE Advanced Files
                
                # Lightweight file managers
                'pcmanfm',  # LXDE/LXQt Files
                'pcmanfm-qt',  # LXQt Files
                'thunar',  # Xfce Files
                
                # Terminal-based file managers
                'ranger',  # Terminal ranger
                'mc',  # Midnight Commander
                'nnn',  # Terminal nnn
                'vifm',  # Vim-like file manager
                'lf',  # List Files
                
                # Alternative desktop environments
                'deepin-file-manager',  # Deepin
                'elementary-files',  # elementary OS
                
                # Shell commands
                'bash', 'zsh', 'sh', 'fish', 'dash', 'ksh', 'tcsh',  # Shells
                'ls', 'cd', 'dir',  # Directory commands
            }
            
            # Method 1: Use lsof to detect directory access (faster, no +D)
            try:
                result = subprocess.run(
                    ['lsof', folder_path],  # Just check the folder itself, not recursively
                    capture_output=True,
                    text=True,
                    timeout=0.5  # Reduced timeout
                )
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        # Parse first match
                        parts = lines[1].split()
                        if len(parts) >= 2:
                            pid = int(parts[1])
                            proc = psutil.Process(pid)
                            proc_name = proc.name()
                            
                            # Return any process (not just file managers)
                            info = f" [Process: {proc_name} (PID: {pid})]"
                            return (info, pid)
            except:
                pass
            
            # Method 2: Check running file managers and see if they have the folder open
            for proc in psutil.process_iter(['pid', 'name', 'cwd']):
                try:
                    proc_name = proc.info.get('name', '')
                    if proc_name in FILE_MANAGERS:
                        # Check if process current working directory is the locked folder
                        cwd = proc.info.get('cwd', '')
                        if cwd and (cwd == folder_path or cwd.startswith(folder_path + os.sep)):
                            pid = proc.info['pid']
                            info = f" [Process: {proc_name} (PID: {pid})]"
                            return (info, pid)
                except:
                    continue
            
            return ("", None)
        except Exception:
            return ("", None)
    
    def _detect_folder_access_windows(self, folder_path: str) -> tuple:
        """
        Windows-specific folder access detection
        Uses Windows API and process enumeration to detect Explorer and other file managers
        """
        try:
            import psutil
            
            # COMPREHENSIVE list of Windows file managers
            FILE_MANAGERS = {
                # Built-in Windows
                'explorer.exe',  # Windows Explorer (default)
                'cmd.exe',  # Command Prompt
                'powershell.exe',  # PowerShell
                'pwsh.exe',  # PowerShell Core
                
                # Third-party file managers
                'TotalCmd64.exe', 'TOTALCMD.EXE',  # Total Commander
                'FreeCommander.exe',  # Free Commander
                'XYplorer.exe',  # XYplorer
                'DirectoryOpus.exe', 'dopus.exe',  # Directory Opus
                'Q-Dir.exe',  # Q-Dir
                'OneCommander.exe',  # One Commander
                'Files.exe',  # Files App (UWP)
                'MultiCommander.exe',  # Multi Commander
                'Altap.exe',  # Altap Salamander
                'xplorer2.exe',  # xplorer²
                
                # Alternative shells
                'Double Commander.exe',  # Double Commander
                'Far.exe',  # Far Manager
            }
            
            # Normalize path for Windows
            folder_path_lower = os.path.abspath(folder_path).lower()
            
            # Method 1: Check open file handles (similar to lsof on Linux)
            # Note: This requires pywin32, fallback to process enumeration if not available
            try:
                import win32api
                import win32file
                import win32con
                
                # Try to open the folder to see if it's in use
                try:
                    handle = win32file.CreateFile(
                        folder_path,
                        win32con.GENERIC_READ,
                        0,  # No sharing - will fail if folder is open
                        None,
                        win32con.OPEN_EXISTING,
                        win32file.FILE_FLAG_BACKUP_SEMANTICS,  # Required for directories
                        None
                    )
                    win32api.CloseHandle(handle)
                except:
                    # Folder is in use - find the process
                    for proc in psutil.process_iter(['pid', 'name', 'exe']):
                        try:
                            proc_name = proc.info.get('name', '').lower()
                            if proc_name in [fm.lower() for fm in FILE_MANAGERS]:
                                # Windows Explorer found - assume it's accessing the folder
                                pid = proc.info['pid']
                                info = f" [Process: {proc.info['name']} (PID: {pid})]"
                                return (info, pid)
                        except:
                            continue
            except ImportError:
                pass  # Fall through to Method 2
            
            # Method 2: Check running file managers and their open handles
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cwd']):
                try:
                    proc_name = proc.info.get('name', '')
                    if proc_name in FILE_MANAGERS:
                        # Check current working directory
                        try:
                            cwd = proc.info.get('cwd', '')
                            if cwd and os.path.abspath(cwd).lower() == folder_path_lower:
                                pid = proc.info['pid']
                                info = f" [Process: {proc_name} (PID: {pid})]"
                                return (info, pid)
                        except:
                            pass
                        
                        # Check open files for this process
                        try:
                            p = psutil.Process(proc.info['pid'])
                            for file_obj in p.open_files():
                                if file_obj.path.lower().startswith(folder_path_lower):
                                    pid = proc.info['pid']
                                    info = f" [Process: {proc_name} (PID: {pid})]"
                                    return (info, pid)
                        except:
                            pass
                except:
                    continue
            
            return ("", None)
        except Exception:
            return ("", None)
    
    def on_modified(self, event: FileSystemEvent):
        """Called when a file is modified"""
        if not event.is_directory and self._is_locked_path(event.src_path):
            if self._should_process_event(event.src_path):
                # CRITICAL: Check if file is already unlocked (skip if already accessible)
                if self._is_file_unlocked(event.src_path):
                    return  # File is unlocked, allow access without prompting
                
                # CRITICAL: Only proceed if we detect a process accessing the file
                proc_info, pid = self._get_process_info(event.src_path)
                
                # If no process detected, ignore this event (likely internal filesystem activity)
                if not pid:
                    return
                
                # Check if file is inside a locked folder
                locked_folder = self._get_locked_parent_folder(event.src_path)
                if locked_folder:
                    # Check if folder is unlocked
                    if self._is_file_unlocked(locked_folder):
                        return  # Folder is unlocked, allow access
                    
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
                # CRITICAL: Check if file is already unlocked
                if self._is_file_unlocked(event.src_path):
                    return  # File is unlocked, allow access
                
                # CRITICAL: Only proceed if we detect a process accessing the file
                proc_info, pid = self._get_process_info(event.src_path)
                
                # If no process detected, ignore this event
                if not pid:
                    return
                
                # Check if file is inside a locked folder
                locked_folder = self._get_locked_parent_folder(event.src_path)
                if locked_folder:
                    if self._is_file_unlocked(locked_folder):
                        return  # Folder is unlocked, allow access
                    
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
                # CRITICAL: Check if file is already unlocked
                if self._is_file_unlocked(event.src_path):
                    return  # File is unlocked, allow access
                
                # CRITICAL: Only proceed if we detect a process accessing the file
                proc_info, pid = self._get_process_info(event.src_path)
                
                # If no process detected, ignore this event
                if not pid:
                    return
                
                # Check if file is inside a locked folder
                locked_folder = self._get_locked_parent_folder(event.src_path)
                if locked_folder:
                    if self._is_file_unlocked(locked_folder):
                        return  # Folder is unlocked, allow access
                    
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
    
    def __init__(self, file_lock_manager, password_callback: Callable, get_state_func: Callable = None, set_state_func: Callable = None, log_activity_func: Callable = None):
        """
        Initialize the file access monitor
        
        Args:
            file_lock_manager: The FileLockManager instance
            password_callback: Function to call for password verification
                              Signature: callback(file_path) -> bool (True if access granted)
            get_state_func: Function to get monitoring state (returns dict with 'unlocked_files')
            set_state_func: Function to update monitoring state
            log_activity_func: Function to log activity events (takes event_type, item_name, item_type, success, details)
        """
        self.file_lock_manager = file_lock_manager
        self.password_callback = password_callback
        self.get_state = get_state_func if get_state_func else lambda: {}
        self.set_state = set_state_func if set_state_func else lambda key, value: None
        self.log_activity_func = log_activity_func
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
            on_access_callback=self._handle_file_access,
            get_state_func=self.get_state  # Pass state function to check unlocked files
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
        print(f"🚀 [MONITOR] Auto-lock thread started (daemon={self.auto_lock_thread.daemon})")
        
        print(f"✅ File access monitoring started for {len(self.monitored_paths)} items")
        print(f"📊 [MONITOR] Status: observer={self.observer is not None}, handler={self.event_handler is not None}, monitoring={self.is_monitoring}")
        return True
    
    def _auto_lock_loop(self):
        """
        Background thread that checks unlocked files and re-locks them when not in use
        Also monitors locked folders for file manager access attempts
        Similar to unified_monitor's auto-lock logic
        
        PERFORMANCE OPTIMIZED: Polling interval 2.0s (was 0.5s)
        Now only checking folders + auto-lock since watchdog handles file detection instantly!
        """
        import subprocess
        
        check_counter = 0  # Counter for less frequent checks
        print(f"🚀 [AUTO-LOCK] Loop started! monitoring={self.is_monitoring}, handler={self.event_handler is not None}")
        
        while self.auto_lock_running:
            try:
                time.sleep(2.0)  # Check every 2 seconds (only for folder checks + auto-lock)
                check_counter += 1
                
                # Debug: Log periodically to confirm loop is running
                if check_counter == 1:
                    print(f"🔄 [AUTO-LOCK] First cycle - checking folders...")
                elif check_counter % 30 == 0:  # Every 60 seconds (30 cycles × 2s)
                    print(f"🔄 [AUTO-LOCK] Still alive (cycle {check_counter})")
                
                # Part 1: Check for folder access attempts (watchdog backup for file managers)
                self._check_locked_folders()
                
                # Part 2: Auto-lock unlocked files (re-lock after timeout)
                # Check every 2 cycles (3 seconds) to reduce CPU usage
                if check_counter % 2 == 0:
                    self._check_auto_lock_files()
                
                # REMOVED: _check_locked_files() polling - watchdog's on_opened() handles this INSTANTLY!
                # The on_opened() event fires immediately when files are accessed (IN_OPEN inotify event)
                # Polling was causing delays and wasting CPU - watchdog is already instant!
                    
            except Exception as e:
                print(f"⚠️  [AUTO-LOCK] Error in auto-lock loop: {e}")
                import traceback
                traceback.print_exc()
    
    def _check_auto_lock_files(self):
        """Check unlocked files and re-lock them when not in use"""
        import subprocess
        
        state = self.get_state()
        unlocked_files = state.get('unlocked_files', [])
        
        if not unlocked_files:
            return
                
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
                
                # Log the auto-lock event for statistics tracking
                if self.log_activity_func:
                    item_type = 'folder' if is_dir else 'file'
                    self.log_activity_func(
                        'lock',
                        filename,
                        item_type,
                        success=True,
                        details='Auto-locked after 10 seconds of inactivity'
                    )
                
            except Exception as e:
                print(f"⚠️  [AUTO-LOCK] Could not re-lock {os.path.basename(file_path)}: {e}")
    
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
    
    def _check_locked_folders(self):
        """
        Periodically check if any file manager is accessing locked folders
        This is needed because watchdog doesn't detect directory browsing
        """
        import os
        
        # Skip if not monitoring or no event handler
        if not self.is_monitoring or not self.event_handler:
            return
        
        # Get list of locked folders
        locked_folders = [item['path'] for item in self.file_lock_manager.locked_items 
                         if item['type'] == 'folder']
        
        state = self.get_state()
        unlocked_files = state.get('unlocked_files', [])
        
        for folder_path in locked_folders:
            # Skip if folder is already unlocked
            if folder_path in unlocked_files:
                continue
            
            # Skip if folder doesn't exist
            if not os.path.exists(folder_path):
                continue
            
            # Detect if file manager is accessing this folder
            proc_info, pid = self.event_handler._detect_folder_access(folder_path)
            
            if pid:  # File manager detected
                folder_name = os.path.basename(folder_path)
                print(f"🔒 Locked folder access detected: {folder_path}{proc_info}")
                
                # Show password dialog
                unlocked = self.password_callback(folder_path)
                
                if not unlocked:
                    # Kill the file manager process
                    self.event_handler._kill_process_accessing_file(folder_path)
    
    def _check_locked_files(self):
        """
        Periodically check if any process is accessing locked files.
        
        CRITICAL: This polling is REQUIRED because:
        - Files are locked with chmod 444 (read-only)
        - Watchdog's on_modified() only fires when files are WRITTEN to
        - Opening files for READING doesn't trigger any filesystem events
        - Without this polling, users can open and read locked files freely
        
        PERFORMANCE OPTIMIZED: Uses BATCH checking to scan all processes ONCE
        instead of calling per-file. This reduces CPU usage dramatically!
        """
        import os
        
        # Skip if not monitoring or no event handler
        if not self.is_monitoring or not self.event_handler:
            return
        
        # Get list of locked files (not folders) that need checking
        all_locked_files = [item['path'] for item in self.file_lock_manager.locked_items 
                           if item['type'] == 'file']
        
        if not all_locked_files:
            return
        
        # Debug: Log first check
        if not hasattr(self, '_first_file_check_done'):
            print(f"🔍 [FILE CHECK] First check - {len(all_locked_files)} locked files")
            self._first_file_check_done = True
        
        state = self.get_state()
        unlocked_files = state.get('unlocked_files', [])
        
        # Filter to only check files that exist and are not already unlocked
        files_to_check = []
        for file_path in all_locked_files:
            if file_path not in unlocked_files and os.path.exists(file_path):
                files_to_check.append(file_path)
        
        if not files_to_check:
            return
        
        # PERFORMANCE: Batch check all files in ONE process scan instead of per-file!
        # This is 10-20x faster than calling _get_processes_using_file() per file
        file_to_pids = self.file_lock_manager._get_processes_using_files(files_to_check)
        
        # Now handle any files that have processes accessing them
        for file_path, pids in file_to_pids.items():
            if not pids:
                continue  # No process accessing this file
            
            if pids:  # Process(es) detected accessing the file
                import psutil
                # Get first process for info display
                try:
                    proc = psutil.Process(pids[0])
                    proc_name = proc.name()
                    proc_info = f" [Process: {proc_name} (PID: {pids[0]})]"
                except:
                    proc_info = f" [PID: {pids[0]}]"
                
                # Debounce check - only show dialog if we haven't checked this file recently
                if self.event_handler._should_process_event(file_path):
                    print(f"🔒 Locked file access detected: {file_path}{proc_info}")
                    
                    # Show password dialog
                    unlocked = self.password_callback(file_path)
                    
                    if not unlocked:
                        # Kill ALL processes accessing the file
                        for pid in pids:
                            try:
                                proc = psutil.Process(pid)
                                proc_name = proc.name()
                                print(f"   🔪 Killing process {pid} ({proc_name})")
                                proc.kill()
                            except:
                                pass
    
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
