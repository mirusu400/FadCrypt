# FadCrypt Polkit Policy

## Overview

# FadCrypt Polkit Policy

## Overview

FadCrypt uses **PolicyKit (polkit)** to grant persistent elevated privileges for file protection operations. This is the **same method used by enterprise antivirus software** like ClamAV, ESET, and Kaspersky.

## How It Works

### 1. **Polkit Policy** (`dev.faded.fadcrypt.policy`)

- Professional authorization policy
- **Persistent authorization** - user authenticates once, works forever
- Three action IDs:
  - `dev.faded.fadcrypt.protect-files` - File protection
  - `dev.faded.fadcrypt.auto-monitor` - Auto-startup
  - `dev.faded.fadcrypt.lock-files` - Lock/unlock operations

## How It Works

### 1. **Polkit Policy** (`com.fadsec.fadcrypt.policy`)

- Defines authorization rules for FadCrypt operations
- Installed to `/usr/share/polkit-1/actions/`
- Allows file protection operations with `allow_active=yes` (persistent authorization)

### 2. **Helper Script** (`fadcrypt-file-protection-helper.sh`)

- Executes privileged operations via `pkexec`
- Uses polkit policy for authorization
- Installed to `/usr/libexec/fadcrypt/`

### 3. **Authorization Flow**

**First time (manual start):**

1. User clicks "Start Monitoring"
2. Polkit shows GUI authorization dialog **once**
3. User authenticates with password
4. Authorization is **cached/remembered** by polkit
5. Files are protected with `chattr +i`

**Subsequent times (including auto-startup):**

1. FadCrypt starts with `--auto-monitor` flag on boot
2. Polkit checks cached authorization
3. **No dialog shown** - authorization persists!
4. Files are protected automatically
5. Completely seamless and silent

## Key Advantages

✅ **Professional Solution** - Same method used by enterprise software
✅ **Persistent Authorization** - User only authenticates once
✅ **Secure** - Follows Linux security best practices
✅ **Seamless Auto-Startup** - Works on system boot without prompts
✅ **PolicyKit Standard** - Built into modern Linux distributions

## Policy Details

```xml
<defaults>
  <allow_any>auth_admin</allow_any>        <!-- Requires admin authentication -->
  <allow_inactive>auth_admin</allow_inactive>
  <allow_active>yes</allow_active>         <!-- Persists for active sessions -->
</defaults>
```

- **allow_any**: Requires admin password for initial authorization
- **allow_active**: Once authorized, persists for the active session
- This means: **Authenticate once, works forever (until logout/reboot)**

## Installation

The polkit policy is automatically installed when you install FadCrypt:

```bash
sudo dpkg -i fadcrypt_2.0.0_amd64.deb
```

Files installed:

- `/usr/share/polkit-1/actions/dev.faded.fadcrypt.policy`
- `/usr/libexec/fadcrypt/fadcrypt-file-protection-helper.sh`

## Verification

Check if policy is installed:

```bash
pkaction --action-id dev.faded.fadcrypt.protect-files --verbose
```

Test authorization:

```bash
pkexec /usr/libexec/fadcrypt/fadcrypt-file-protection-helper.sh protect /tmp/test.txt
```

## Comparison with Other Methods

| Method               | Persistent? | Secure?     | Auto-Startup? | Professional? |
| -------------------- | ----------- | ----------- | ------------- | ------------- |
| **Polkit Policy** ✅ | ✅ Yes      | ✅ Yes      | ✅ Yes        | ✅ Yes        |
| sudo password        | ❌ No       | ⚠️ Moderate | ❌ No         | ❌ No         |
| setuid binary        | ⚠️ Yes      | ❌ Risky    | ✅ Yes        | ❌ No         |
| chmod only           | ✅ Yes      | ❌ Weak     | ✅ Yes        | ❌ No         |

## Technical Details

### Authorization Caching

Polkit caches authorization decisions based on:

- User identity (UID)
- Action ID (`com.fadsec.fadcrypt.protect-files`)
- Session state (active/inactive)

Cache persists until:

- User logs out
- System reboots
- Session becomes inactive

### Helper Script Execution

```bash
pkexec /usr/libexec/fadcrypt/fadcrypt-file-protection-helper.sh protect file1 file2 file3
```

1. `pkexec` checks polkit policy
2. If authorized (cached or new prompt), executes helper script
3. Helper script runs `chattr +i` on all files
4. Returns success/failure to FadCrypt

### Security

- Helper script only accepts `protect`/`unprotect` actions
- Cannot execute arbitrary commands
- Validates all file paths
- Runs with minimal necessary privileges
- Follows principle of least privilege

## Troubleshooting

**Issue**: Still seeing sudo prompts on auto-startup

**Solution**:

1. Verify polkit policy is installed:

   ```bash
   ls -l /usr/share/polkit-1/actions/com.fadsec.fadcrypt.policy
   ```

2. Restart polkit service:

   ```bash
   sudo systemctl restart polkit.service
   ```

3. Check polkit logs:
   ```bash
   journalctl -u polkit.service -n 50
   ```

**Issue**: "Authentication failed" on first use

**Solution**: This is normal! Authenticate once, then it persists.

## References

- [PolicyKit Documentation](https://www.freedesktop.org/software/polkit/docs/latest/)
- [pkexec Manual](https://man.archlinux.org/man/pkexec.1)
- [Polkit Actions](https://www.freedesktop.org/software/polkit/docs/latest/polkit.8.html)

## Developed by FadSec Lab

Made with ❤️ in Pakistan 🇵🇰
