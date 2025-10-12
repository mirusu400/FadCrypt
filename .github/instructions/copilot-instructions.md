## Quick orientation for AI coding agents

This repository implements FadCrypt — a cross-platform (Windows + Linux) GUI app written in Python (Tkinter/ttkbootstrap) that locks/monitors applications and persists encrypted configuration.

Read these files first to understand structure and entry points:

- `FadCrypt.py` — Windows-focused entrypoint and primary implementation (uses `winreg`, `ctypes`, `.exe` handling).
- `FadCrypt_Linux.py` — Linux-specific variant (uses `fcntl`, `.desktop` autostart, ELF/executable detection).
- `README.md` — install/build instructions and dependency list.
- `FadCrypt.spec` — PyInstaller packaging configuration used to create installers.

Big-picture notes (why things are split):

- Platform-specific behavior is implemented by maintaining two near-duplicate entry scripts: `FadCrypt.py` (Windows) and `FadCrypt_Linux.py` (Linux). When changing core behavior, mirror changes to both files unless the change is intentionally platform-specific.
- UI is Tkinter + `ttkbootstrap`. The project vendors a local `ttkbootstrap/` package — treat it as part of the repo (don't assume it's the upstream pip package when editing styles/components).
- Packaging relies on PyInstaller and `FadCrypt.spec`. The code uses `resource_path()` which expects PyInstaller's `_MEIPASS` at runtime.

Data, persistence and conventions:

- Config and state files are accessed via `get_fadcrypt_folder()` (search usages in `AppLocker`). On Windows, sensitive files live under `AppData\Roaming\FadCrypt` and backups under `C:\ProgramData\FadCrypt\Backup` (refer to `README.md`).
- The app stores an encrypted password file named `encrypted_password.bin` (mentioned in README) — treat this as a critical artifact when modifying crypto or migration logic.
- Versioning is manual via `__version__` and `__version_code__` at the top of each entry script — bump both when releasing.

Important runtime flags and behaviors:

- `--auto-monitor` — entry scripts check for this flag and call startup-monitoring flow immediately.
- Single-instance enforcement: Linux uses a lock-file pattern (see `/tmp/fadcrypt.lock` and imports of `fcntl`); Windows uses mutex-like mechanisms. Be careful editing the single-instance logic — the app enforces process-level prevention.

Dependencies & how to run locally (from `README.md`):

- Install deps: `pip install cryptography psutil pillow pystray watchdog tkinterdnd2 ttkbootstrap pygame requests`
- Run on Linux: `python3 FadCrypt_Linux.py`.
- Build distributable: `python3 -m PyInstaller FadCrypt.spec` (spec file is configured for windows/linux differences).

Patterns and common change routines for contributors / agents:

- When editing UI widgets, update both `create_widgets()` implementations in `FadCrypt.py` and `FadCrypt_Linux.py` unless the change should only affect one platform.
- Resource loading uses `resource_path(relative)` to support PyInstaller; use it when referencing files from `img/` or packaged assets.
- Platform-conditional code is handled by separate files rather than runtime branching. To add a platform abstraction, prefer extracting logic into a shared module and call from both entry scripts.

Safe-change checklist for agents (minimal, actionable):

1. Install dependencies: `python -m pip install -r requirements` (or install the list above).
2. Run the app locally for quick smoke checks: `python3 FadCrypt_Linux.py` (or run the Windows entrypoint on Windows).
3. Make small, focused changes and verify the UI and persistence behavior manually. If changing persistence/crypto, export a migration plan and add automated checks.
4. When adding UI assets, use `resource_path()` and include them under `img/`.

Where to look for examples in the codebase:

- Autostart creation (Linux): search for `--auto-monitor` and the `.desktop` creation logic in `FadCrypt_Linux.py`.
- Single-instance lock: search for `fcntl`, `/tmp/fadcrypt.lock`, and any `SingleInstance` class definitions.
- Drag-and-drop and executable detection: look at `on_drop()` and `is_elf_binary()` in `FadCrypt_Linux.py`.

If anything in this file is unclear or you need more specifics (packaging targets, CI steps, or where persistent state is created), tell me which area you want expanded and I will iterate.
