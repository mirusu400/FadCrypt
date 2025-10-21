# Windows Privilege Elevation System (PolicyKit Equivalent)

## Overview

FadCrypt for Windows implements a professional privilege escalation system that is functionally equivalent to the Linux PolicyKit solution. This provides seamless, persistent elevation for critical operations without repeated UAC prompts.

**Key Features:**

- ✅ **Persistent Authorization**: Single authentication per session (like PolicyKit's allow_active=yes)
- ✅ **Professional Approach**: Uses Windows Task Scheduler instead of crude UAC prompts
- ✅ **Minimal User Friction**: Caches elevated session for all subsequent operations
- ✅ **Secure Execution**: Runs with SYSTEM privileges via Task Scheduler
- ✅ **Cross-Platform Compatibility**: Works on Windows 7 SP1+ and Windows Server 2008 R2+

## Architecture

### 1. **Windows Elevation Manager** (`core/windows/elevation_manager.py`)

The `WindowsElevationManager` class handles all privilege elevation logic:

```python
# Get the manager
manager = get_elevation_manager()

# Execute elevated operations
success, error = manager.disable_system_tools()
success, error = manager.protect_files([file1, file2])
```

**Features:**

- Task Scheduler approach (preferred, persistent)
- UAC fallback (if Task Scheduler unavailable)
- Helper script injection for maximum compatibility

### 2. **Elevated Helper Script** (`core/windows/fadcrypt-elevated-helper.py`)

Standalone script that executes as SYSTEM via Task Scheduler:

**Operations Supported:**

- `disable-tools` - Disable Command Prompt, Task Manager, Registry Editor, Control Panel
- `enable-tools` - Re-enable previously disabled tools
- `protect-files` - Set file attributes (HIDDEN, SYSTEM, READONLY)
- `unprotect-files` - Remove file protection attributes

## Installation & Setup

### For Developers (Testing on Windows)

1. **Files already created:**

   - `core/windows/elevation_manager.py`
   - `core/windows/fadcrypt-elevated-helper.py`

2. **Update `core/file_protection.py`** to use Windows elevation:

```python
if IS_WINDOWS:
    from core.windows.elevation_manager import get_elevation_manager

    manager = get_elevation_manager()
    success, error = manager.protect_files([file_path])
    # Check success/error
```

3. **Update system tool disabling** in `ui/windows/main_window_windows.py`:

```python
from core.windows.elevation_manager import get_elevation_manager

def disable_tools(self):
    manager = get_elevation_manager()
    success, error = manager.disable_system_tools()
    if success:
        print("✅ System tools disabled")
    else:
        print(f"❌ Error: {error}")
```

### For Package Distribution

When building .exe with PyInstaller:

1. **Include helper script in spec file:**

```python
# In FadCrypt.spec
datas=[
    ('core/windows/fadcrypt-elevated-helper.py', 'core/windows'),
    # ... other files
]
```

2. **Update MSI/InnoSetup installer** to handle Task Scheduler permissions

3. **Optional: Embed manifest** for automatic elevation (alternative method)

## How It Works (Technical Details)

### Scenario 1: Disable System Tools (During Monitoring Start)

```
User clicks "Start Monitoring"
    ↓
File Protection check needed? YES
    ↓
Windows Elevation Manager detects elevation needed
    ↓
Try Task Scheduler approach:
    1. Generate scheduled task XML with operation details
    2. Register task via schtasks.exe /create
    3. Run task via schtasks.exe /run [SYSTEM privileges]
    4. Task Scheduler prompts user with UAC once
    5. Task executes elevated helper script
    6. Helper processes operation (disable tools, protect files)
    7. Caches SYSTEM context for session
    8. Delete temporary task
    ↓
If Task Scheduler unavailable:
    1. Fallback to direct UAC via ShellExecuteW "runas"
    2. User prompted with UAC dialog
    ↓
Success → Continue monitoring
Failure → Show error, ask user to run as admin
```

### Scenario 2: Subsequent Operations (Same Session)

```
User attempts another operation requiring elevation
    ↓
Windows Elevation Manager asked again
    ↓
Task Scheduler approach:
    1. Register another task
    2. Run it (NO UAC prompt - Session already elevated!)
    3. Executes immediately
    ↓
Result: Multiple operations with single UAC prompt
```

## Advantages Over Alternatives

### vs. "Run as Administrator" at Startup

**Problem:** Entire app runs as admin (security risk)
**Our solution:** Only privileged operations run elevated

### vs. UAC Prompts for Every Operation

**Problem:** Poor UX, user fatigue
**Our solution:** Single UAC prompt, cached session

### vs. Manifest-Only Elevation

**Problem:** Requires .exe rebuild, can't toggle elevation
**Our solution:** Runtime-based elevation, flexible

## File Attributes System (Windows Equivalent of chattr +i)

### Setting Protection

```python
# Equivalent to: chattr +i /path/to/file (Linux)
# Windows: Set attributes HIDDEN | SYSTEM | READONLY

FILE_ATTRIBUTE_HIDDEN    = 0x00000002
FILE_ATTRIBUTE_SYSTEM    = 0x00000004
FILE_ATTRIBUTE_READONLY  = 0x00000001

# Apply all three for maximum protection
new_attrs = FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM | FILE_ATTRIBUTE_READONLY
SetFileAttributesW(file_path, new_attrs)
```

### Effect

- File hidden in normal view
- User can't delete (readonly flag)
- Requires elevated privileges to modify
- Survives reboot

### Removing Protection

```python
# Remove protection attributes
FILE_ATTRIBUTE_NORMAL = 0x00000080

new_attrs = current_attrs & ~(HIDDEN | SYSTEM | READONLY)
new_attrs |= FILE_ATTRIBUTE_NORMAL

SetFileAttributesW(file_path, new_attrs)
```

## Registry Operations for Tool Disabling

### Disable Command Prompt

```
HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\System
  DisableCMD = 1 (REG_DWORD)
```

### Disable Task Manager

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\System
  DisableTaskMgr = 1 (REG_DWORD)
```

### Disable Registry Editor

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\System
  DisableRegistryTools = 1 (REG_DWORD)
```

### Disable Control Panel

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer
  NoControlPanel = 1 (REG_DWORD)
```

### Disable PowerShell Execution

```
HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\PowerShell
  ExecutionPolicy = 0 (REG_DWORD)  [0=Restricted, 1=AllSigned, 2=RemoteSigned, 3=Unrestricted]
```

These are re-enabled by deleting the values or setting to appropriate default values.

## Error Handling & Fallbacks

```python
# Best case: Task Scheduler (persistent, no repeated prompts)
# ↓ Fails if schtasks.exe unavailable
# Fallback 1: Direct UAC ShellExecuteW (single prompt)
# ↓ Fails if not running on Windows or ctypes unavailable
# Fallback 2: Warning to user (no elevation possible)
```

## Security Considerations

### ✅ Secure Design

- Helper script validates all operations
- Task Scheduler runs as SYSTEM (highest privilege, isolated)
- Operations logged for audit trail
- No plaintext passwords in task XML
- Temporary tasks deleted after execution

### ⚠️ Limitations

- Windows only (by design)
- Requires Windows Vista or later (Task Scheduler v2)
- Some antivirus software may block Task Scheduler API
- User must have administrator account (not required to be current user)

### 🔒 Recommendations

- Run app with limited user (elevation only when needed)
- Monitor Task Scheduler for any unauthorized use
- Regularly review disabled tools settings
- Uninstall properly to re-enable tools

## Testing on Linux (Mock Mode)

For development on Linux (cross-platform testing):

```python
python3 FadCrypt.py --windows  # Enable mock Windows mode
```

This loads mock implementations from `win_compat.py` and `win_mock.py`.

## Comparison: Linux vs Windows

| Feature               | Linux (PolicyKit)           | Windows (Task Scheduler)                 |
| --------------------- | --------------------------- | ---------------------------------------- |
| **Elevation Method**  | Polkit authorization        | Windows Task Scheduler                   |
| **Privilege Level**   | Requested per operation     | Cached per session                       |
| **File Immutability** | `chattr +i` (filesystem)    | File attributes (HIDDEN/SYSTEM/READONLY) |
| **System Tool Lock**  | `chmod 000` + `chattr +i`   | Registry policies                        |
| **Persistence**       | `allow_active=yes`          | Task Scheduler session                   |
| **User Experience**   | One sudo prompt per session | One UAC prompt per session               |
| **Availability**      | Linux 3.0+                  | Windows Vista+                           |
| **Complexity**        | Lower (polkit built-in)     | Higher (Task Scheduler XML)              |

## Implementation Checklist

- [ ] Create `core/windows/elevation_manager.py` ✅
- [ ] Create `core/windows/fadcrypt-elevated-helper.py` ✅
- [ ] Update `core/file_protection.py` to use elevation manager
- [ ] Update Windows main window to use elevation manager
- [ ] Add elevation manager import to Windows UI components
- [ ] Test on Windows 10/11 with UAC enabled
- [ ] Update PyInstaller spec to include helper script
- [ ] Create Windows installer with proper permissions
- [ ] Update README with Windows setup instructions
- [ ] Add comprehensive logging for debugging

## Troubleshooting

### Issue: UAC Prompt Appears Every Time

**Cause:** Task Scheduler not available/failing
**Solution:** Check that schtasks.exe exists (C:\Windows\System32\schtasks.exe)

### Issue: "Access Denied" Error

**Cause:** Not running with admin account
**Solution:** Run FadCrypt as administrator

### Issue: Task Scheduler Timeout

**Cause:** Slow system or large file operations
**Solution:** Increase timeout in Task XML (currently 1 hour)

### Issue: Tools Still Accessible After Disable

**Cause:** Registry settings insufficient alone
**Solution:** Need to run as admin to set restrictions

## Future Enhancements

1. **COM API Integration** - More modern than Task Scheduler
2. **Windows Service** - Persistent elevated service running in background
3. **Driver-Level Protection** - File system filter driver (complex, enterprise-grade)
4. **Azure AD Integration** - For enterprise MDM scenarios

## References

- [Windows Task Scheduler XML Schema](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-schema)
- [ShellExecuteW Function](https://docs.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutew)
- [File Attributes Constants](https://docs.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants)
- [Windows Registry Group Policy](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings)
