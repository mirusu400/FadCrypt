# Building FadCrypt .deb Package for Linux

## Prerequisites

Install PyInstaller and dependencies:

```bash
pip install pyinstaller cryptography psutil pillow pystray watchdog tkinterdnd2 ttkbootstrap pygame requests
```

## Build Process

1. **Build the .deb package:**

   ```bash
   ./build-deb.sh
   ```

2. **Install the package:**

   ```bash
   sudo dpkg -i fadcrypt_X.X.X_amd64.deb
   ```

3. **Run FadCrypt:**
   ```bash
   fadcrypt
   ```
   Or launch from application menu.

## Uninstall

```bash
sudo dpkg -r fadcrypt
```

## Package Structure

After installation:

- Binary: `/usr/bin/fadcrypt`
- Desktop file: `/usr/share/applications/fadcrypt.desktop`
- Icon: `/usr/share/pixmaps/fadcrypt.png`
- Documentation: `/usr/share/doc/fadcrypt/`

## Auto-start

When you enable monitoring in FadCrypt, it will create:

- `~/.config/autostart/FadCrypt.desktop` with `Exec=fadcrypt --auto-monitor`

This ensures FadCrypt starts automatically on login using the installed command.
