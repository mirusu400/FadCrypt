"""
Windows Compatibility Layer for Linux Testing
This module provides mock implementations of Windows-specific modules
so the Windows version can be tested on Linux for GUI development.
"""

import sys
import os

# Set up Windows environment variables for Linux
if sys.platform.startswith('linux'):
    # Mock APPDATA directory
    home = os.path.expanduser('~')
    if 'APPDATA' not in os.environ:
        os.environ['APPDATA'] = os.path.join(home, '.local', 'share')
    if 'LOCALAPPDATA' not in os.environ:
        os.environ['LOCALAPPDATA'] = os.path.join(home, '.local', 'share')
    if 'PROGRAMDATA' not in os.environ:
        os.environ['PROGRAMDATA'] = os.path.join(home, '.local', 'share')

# Mock winreg module
class MockWinReg:
    HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
    HKEY_LOCAL_MACHINE = "HKEY_LOCAL_MACHINE"
    KEY_SET_VALUE = 0x0002
    KEY_READ = 0x20019
    REG_SZ = 1
    REG_DWORD = 4
    
    @staticmethod
    def OpenKey(key, sub_key, reserved=0, access=0):
        print(f"[MOCK] OpenKey: {key}\\{sub_key}")
        return "mock_key"
    
    @staticmethod
    def SetValueEx(key, value_name, reserved, type, value):
        print(f"[MOCK] SetValueEx: {value_name} = {value}")
    
    @staticmethod
    def DeleteValue(key, value_name):
        print(f"[MOCK] DeleteValue: {value_name}")
    
    @staticmethod
    def CloseKey(key):
        print(f"[MOCK] CloseKey")
    
    @staticmethod
    def QueryValueEx(key, value_name):
        print(f"[MOCK] QueryValueEx: {value_name}")
        return ("mock_value", MockWinReg.REG_SZ)
    
    @staticmethod
    def CreateKey(key, sub_key):
        print(f"[MOCK] CreateKey: {key}\\{sub_key}")
        return "mock_key"

# Mock ctypes.windll
class MockWinDLL:
    class Shell32:
        @staticmethod
        def IsUserAnAdmin():
            print("[MOCK] IsUserAnAdmin: returning True")
            return 1
        
        @staticmethod
        def ShellExecuteW(hwnd, operation, file, parameters, directory, show_cmd):
            print(f"[MOCK] ShellExecuteW: {operation} {file} {parameters}")
            return 42
    
    class User32:
        @staticmethod
        def SystemParametersInfoW(action, param, pvParam, winini):
            print(f"[MOCK] SystemParametersInfoW: action={action}")
            return 1
    
    shell32 = Shell32()
    user32 = User32()

# Patch ctypes if on Linux
if sys.platform.startswith('linux'):
    import ctypes
    if not hasattr(ctypes, 'windll'):
        ctypes.windll = MockWinDLL()

# Install mock winreg
if sys.platform.startswith('linux'):
    sys.modules['winreg'] = MockWinReg()
