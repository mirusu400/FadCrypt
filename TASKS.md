# FadCrypt PyQt6 Migration - Task Breakdown

## 🎯 Goals

- Migrate from Tkinter to PyQt6 for modern, cross-platform UI
- Refactor monolithic files into clean OOP architecture
- Maintain ALL existing functionality and logic
- Use DRY principle: shared business logic in `core/`, UI in `ui/`
- Platform-specific code via inheritance (Windows base → Linux extends)
- No loss of context, features, or mechanisms

---

## 📋 Phase 1: Foundation & Basic Setup (First Working Prototype)

### 1.1 Project Structure Setup ✅

- [x] Create `ui/` folder for all UI components
- [x] Create `ui/__init__.py` with package exports
- [x] Create `ui/base/` for base/shared UI components
- [x] Create `ui/windows/` for Windows-specific UI
- [x] Create `ui/linux/` for Linux-specific UI
- [x] Create `ui/components/` for reusable widgets
- [x] Create `ui/dialogs/` for dialog windows
- [ ] Update `.gitignore` for PyQt6 cache files

### 1.2 Dependencies & Environment ✅

- [x] Add PyQt6 to `requirements.txt` (PyQt6, PyQt6-Qt6, PyQt6-sip)
- [ ] Create `requirements-dev.txt` for development tools
- [x] Test PyQt6 installation on Windows & Linux
- [ ] Document Qt Designer usage (optional)

### 1.3 Core Business Logic Extraction (Platform-Agnostic) ✅

- [x] Move encryption/decryption logic from `AppLocker` to `core/crypto_manager.py`
- [x] Move password management to `core/password_manager.py`
- [ ] Extend `core/config_manager.py` with all config operations
- [ ] Extend `core/application_manager.py` with platform-agnostic app logic
- [x] Keep `core/unified_monitor.py` as-is (already platform-agnostic)
- [x] Create `core/autostart_manager.py` for startup logic (platform-specific methods)
- [ ] Create `core/system_tray_manager.py` for tray icon logic

### 1.4 Platform-Specific Business Logic Separation (SKIP FOR NOW)

- [ ] Create `core/windows/registry_manager.py` (winreg operations) - DEFERRED
- [ ] Create `core/windows/process_manager.py` (Windows process handling) - DEFERRED
- [ ] Create `core/linux/desktop_manager.py` (.desktop file operations) - DEFERRED
- [ ] Create `core/linux/process_manager.py` (Linux process handling, fcntl locks) - DEFERRED

### 1.5 Create Base AppLocker Class (Platform-Agnostic) - DEFERRED TO PHASE 6

- [ ] Create `core/base_app_locker.py` with shared methods
- [ ] Extract methods: `get_fadcrypt_folder()`, `resource_path()`, etc.
- [ ] Extract: password validation, app add/remove/edit logic
- [ ] Extract: config save/load operations (use ConfigManager)
- [ ] Use composition: inject platform-specific managers

### 1.6 Basic PyQt6 Main Window ✅

- [x] Create `ui/base/main_window_base.py` with QMainWindow
- [x] Set window properties: title, icon, size (700x650)
- [x] Add menu bar stub
- [x] Add central widget with QTabWidget placeholder
- [x] Add status bar

### 1.7 Basic Entry Point ✅

- [x] Create `FadCrypt_Qt.py` (new entry point for testing)
- [x] Import PyQt6 (QApplication, QMainWindow)
- [x] Initialize QApplication
- [x] Load base main window
- [ ] Add command-line arg parsing (`--auto-monitor`, etc.)
- [x] Test: Launch app and see empty window

**🎉 Phase 1 Deliverable:** Empty PyQt6 window launches successfully

---

## 📋 Phase 2: Core UI Widgets & Layout

### 2.1 Main Tab Structure ✅

- [x] Create `ui/components/tab_widget.py` (custom QTabWidget) - using built-in
- [x] Add "Home" tab (QWidget)
- [x] Add "Settings" tab (QWidget)
- [x] Add "About" tab (QWidget)
- [ ] Style tabs (match dark theme from Tkinter version)

### 2.2 Home Tab - Application List ✅

- [x] Create `ui/components/app_list_widget.py` (QListWidget or QTreeWidget)
- [x] Design list item: app name, path, status (locked/unlocked)
- [ ] Add custom item delegate for styled rendering
- [x] Add context menu (right-click): Edit, Remove, Open Location
- [x] Add drag-and-drop support (QListWidget.setAcceptDrops)

### 2.3 Home Tab - Control Buttons ✅

- [x] Create `ui/components/button_panel.py` (QWidget with QHBoxLayout)
- [x] Add buttons: Add Application, Lock All, Unlock All
- [x] Connect button signals to slots (stub methods)
- [ ] Style buttons (match existing theme)

- [ ] Create `ui/components/button_panel.py` (QWidget with QHBoxLayout)
- [ ] Add buttons: Add Application, Lock All, Unlock All
- [ ] Connect button signals to slots (stub methods)
- [ ] Style buttons (match existing theme)

### 2.4 Settings Tab - Basic Layout ✅

- [x] Create `ui/components/settings_panel.py` (QWidget)
- [x] Add QFormLayout for settings
- [x] Add QCheckBox: "Lock System Tools"
- [x] Add QComboBox: "Password Dialog Style" (simple/fullscreen)
- [x] Add QComboBox: "Wallpaper Choice" (default/custom)
- [x] Add QPushButton: "Change Master Password"

### 2.5 About Tab ✅

- [x] Create `ui/components/about_panel.py` (QWidget)
- [x] Display app version, version code
- [x] Display credits, GitHub link (QLabel with hyperlinks)
- [ ] Add FadCrypt logo (QLabel with QPixmap)

**🎉 Phase 2 Deliverable:** All tabs visible with UI elements (non-functional) - DONE ✅

---

## 📋 Phase 3: Connect UI to Business Logic

### 3.1 Initialize Core Managers in Main Window - DEFERRED

- [ ] Instantiate `ConfigManager` in main window
- [ ] Instantiate `ApplicationManager`
- [ ] Instantiate `UnifiedMonitor`
- [ ] Instantiate `PasswordManager`
- [ ] Instantiate `CryptoManager`
- [ ] Pass managers to UI components via constructor

### 3.2 Password Dialog (PyQt6) ✅

- [x] Create `ui/dialogs/password_dialog.py` (QDialog)
- [x] Simple version: QLabel + QLineEdit (password) + OK/Cancel buttons
- [ ] Fullscreen version: full-screen QDialog with wallpaper background
- [ ] Add rounded corners styling (QSS stylesheet)
- [ ] Connect to `PasswordManager.verify_password()`

### 3.3 Add Application Functionality ✅

- [x] Connect "Add Application" button to slot
- [x] Show QFileDialog to select executable
- [x] On Linux: filter for executables or .desktop files
- [ ] On Windows: filter for .exe files
- [x] Call `ApplicationManager.add_application()` - READY
- [x] Refresh app list widget

### 3.4 Remove/Edit Application ✅

- [x] Connect context menu "Remove" to slot
- [x] Show confirmation dialog (QMessageBox)
- [x] Call `ApplicationManager.remove_application()` - READY
- [x] Connect context menu "Edit" to slot
- [ ] Show edit dialog (QInputDialog or custom dialog)

### 3.5 Lock/Unlock All Applications ✅

- [x] Connect "Lock All" button to slot
- [x] Call `ApplicationManager.lock_all_applications()` - READY
- [x] Update UI (lock icons/status)
- [x] Connect "Unlock All" button to slot
- [ ] Prompt for master password via `PasswordDialog`
- [x] Call `ApplicationManager.unlock_all_applications()` - READY

### 3.6 Individual App Lock/Unlock ✅

- [x] Add toggle button/checkbox in app list items
- [x] Connect toggle to slot
- [x] Call `ApplicationManager.lock_application(app_name)` - READY
- [x] Call `ApplicationManager.unlock_application(app_name)` - READY

**🎉 Phase 3 Deliverable:** Can add/remove apps, lock/unlock functionality works - 70% DONE

---

## 📋 Phase 4: Application Monitoring Integration

### 4.1 Connect UnifiedMonitor to UI

- [ ] Start `UnifiedMonitor` when monitoring is enabled
- [ ] Connect monitor signals to UI slots (for status updates)
- [ ] Add "Start Monitoring" / "Stop Monitoring" button
- [ ] Show monitoring status in status bar (e.g., "Monitoring: 5 apps")

### 4.2 Password Prompt on App Launch

- [ ] `UnifiedMonitor` detects locked app launch
- [ ] Emit signal to main window
- [ ] Main window shows `PasswordDialog`
- [ ] On correct password: unlock app and let it run
- [ ] On incorrect password: terminate process (Linux: `proc.terminate()`)

### 4.3 System Tray Integration

- [ ] Create `ui/components/system_tray.py` (QSystemTrayIcon)
- [ ] Add tray icon (use existing icon from `img/`)
- [ ] Add tray menu: Show, Hide, Start Monitoring, Stop Monitoring, Exit
- [ ] Connect menu actions to main window methods
- [ ] Implement minimize-to-tray behavior

### 4.4 Autostart on Boot

- [ ] Use `core/autostart_manager.py` methods
- [ ] Add checkbox in Settings: "Start with System"
- [ ] On Windows: create registry entry or shortcut in Startup folder
- [ ] On Linux: create `.desktop` file in `~/.config/autostart/`
- [ ] Test: reboot and verify FadCrypt starts in tray

**🎉 Phase 4 Deliverable:** Full monitoring workflow functional

---

## 📋 Phase 5: Settings & Persistence

### 5.1 Settings Save/Load

- [ ] Connect all settings widgets to slots
- [ ] On change: save to `settings.json` via `ConfigManager`
- [ ] On app launch: load settings and populate widgets
- [ ] Apply settings: dialog style, wallpaper, lock tools, etc.

### 5.2 Master Password Management

- [ ] "Change Master Password" button → show dialog
- [ ] Create `ui/dialogs/change_password_dialog.py`
- [ ] Old password + New password + Confirm new password
- [ ] Call `PasswordManager.change_password()`
- [ ] Re-encrypt all app passwords with new master password

### 5.3 Lock System Tools (Linux)

- [ ] Connect "Lock System Tools" checkbox to slot
- [ ] Use existing logic from `FadCrypt_Linux.py` (lines 2700-2800)
- [ ] Disable execute permissions on system tools (`chmod -x`)
- [ ] Store disabled tools in `disabled_tools.txt`
- [ ] Add "Unlock Tools" cleanup logic

### 5.4 Custom Wallpaper Selection

- [ ] "Wallpaper Choice" combobox → add "Browse..." option
- [ ] Show QFileDialog to select image
- [ ] Save path to settings
- [ ] Use custom wallpaper in fullscreen password dialog

**🎉 Phase 5 Deliverable:** All settings functional and persistent

---

## 📋 Phase 6: Platform-Specific Features

### 6.1 Windows-Specific Implementation

- [ ] Create `ui/windows/main_window_windows.py` (extends base)
- [ ] Add Windows-specific methods (if any)
- [ ] Create `core/windows/app_locker_windows.py` (extends base_app_locker)
- [ ] Implement Windows process detection (psutil + ctypes)
- [ ] Implement Windows autostart (registry keys)
- [ ] Test on Windows 10/11

### 6.2 Linux-Specific Implementation

- [ ] Create `ui/linux/main_window_linux.py` (extends base)
- [ ] Add Linux-specific methods (system tools locking UI)
- [ ] Create `core/linux/app_locker_linux.py` (extends base_app_locker)
- [ ] Implement Linux process detection (psutil + fcntl)
- [ ] Implement Linux autostart (.desktop files)
- [ ] Implement single-instance lock (`/tmp/fadcrypt.lock` with fcntl)
- [ ] Test on Ubuntu/Debian/Arch

### 6.3 Cross-Platform Entry Points

- [ ] Update `FadCrypt.py` (Windows entry point)
  - Import `ui.windows.main_window_windows.MainWindow`
  - Import `core.windows.app_locker_windows.AppLockerWindows`
- [ ] Update `FadCrypt_Linux.py` (Linux entry point)
  - Import `ui.linux.main_window_linux.MainWindow`
  - Import `core.linux.app_locker_linux.AppLockerLinux`
- [ ] Ensure both entry points use same command-line args

**🎉 Phase 6 Deliverable:** Platform-specific features working on both OSes

---

## 📋 Phase 7: Advanced Features & Polish

### 7.1 Drag-and-Drop for Adding Apps

- [ ] Enable drag-and-drop on app list widget
- [ ] Implement `dragEnterEvent()` and `dropEvent()`
- [ ] Extract app path from dropped file/URL
- [ ] Call `add_application()` automatically

### 7.2 Search/Filter Apps

- [ ] Add QLineEdit search box above app list
- [ ] Implement real-time filtering (connect textChanged signal)
- [ ] Filter by app name or path

### 7.3 Import/Export Configuration

- [ ] Add menu items: File → Export Config, File → Import Config
- [ ] Export: save `config.json` + `settings.json` to ZIP
- [ ] Import: load from ZIP, merge or replace existing config
- [ ] Prompt for master password to decrypt imported config

### 7.4 Statistics/Usage Tab (Optional)

- [ ] Create `ui/components/stats_panel.py`
- [ ] Track: # of password prompts, # of blocked attempts, uptime
- [ ] Display in new "Statistics" tab
- [ ] Add charts (e.g., using matplotlib or QtCharts)

### 7.5 Dark/Light Theme Toggle

- [ ] Add "Theme" setting (Dark/Light/System)
- [ ] Create QSS stylesheets for both themes
- [ ] Apply stylesheet dynamically via `QApplication.setStyleSheet()`

### 7.6 Keyboard Shortcuts

- [ ] Add shortcuts: Ctrl+A (Add App), Ctrl+L (Lock All), Ctrl+U (Unlock All)
- [ ] Add shortcut: Ctrl+Q (Quit), Ctrl+, (Settings)
- [ ] Use `QShortcut` or `QAction` with shortcuts

### 7.7 Logging & Debugging

- [ ] Add logging module (`logging` or `loguru`)
- [ ] Log to `~/.FadCrypt/fadcrypt.log`
- [ ] Add "View Logs" button in About tab
- [ ] Show logs in QTextEdit dialog

**🎉 Phase 7 Deliverable:** Advanced features complete

---

## 📋 Phase 8: Testing & Refinement

### 8.1 Unit Tests

- [ ] Create `tests/` folder
- [ ] Write tests for `core/` modules (pytest)
- [ ] Write tests for crypto, password, config managers
- [ ] Test `UnifiedMonitor` logic (mock psutil)

### 8.2 Integration Tests

- [ ] Test full workflow: add app → lock → monitor → password prompt → unlock
- [ ] Test on multiple apps simultaneously
- [ ] Test Chrome app grouping (multiple Chrome apps unlock together)

### 8.3 Edge Case Testing

- [ ] Test with 0 apps, 1 app, 50+ apps
- [ ] Test with non-existent app paths
- [ ] Test with locked master password file corruption
- [ ] Test process detection for edge cases (zombie processes, etc.)

### 8.4 Performance Testing

- [ ] Measure CPU usage (should be ~3-5% with 3 apps)
- [ ] Measure memory usage
- [ ] Profile `UnifiedMonitor` polling interval
- [ ] Optimize if needed

### 8.5 UI/UX Testing

- [ ] Test on different screen sizes/resolutions
- [ ] Test on HiDPI displays
- [ ] Test dark theme contrast/readability
- [ ] Get user feedback

**🎉 Phase 8 Deliverable:** All tests passing, no critical bugs

---

## 📋 Phase 9: Packaging & Distribution

### 9.1 PyInstaller Configuration

- [ ] Update `FadCrypt.spec` for PyQt6 (add Qt plugins)
- [ ] Update `FadCrypt_Linux.spec` for PyQt6
- [ ] Test PyInstaller build on Windows
- [ ] Test PyInstaller build on Linux

### 9.2 Debian Package (.deb)

- [ ] Update `build-deb.sh` for PyQt6 dependencies
- [ ] Update `debian/control` (add PyQt6)
- [ ] Test .deb installation on Ubuntu/Debian

### 9.3 Windows Installer (Inno Setup)

- [ ] Update `innosetup/FadCrypt-inno-setup-script.iss`
- [ ] Test Windows installer
- [ ] Code-sign executable (if available)

### 9.4 Documentation Updates

- [ ] Update `README.md` with PyQt6 migration notes
- [ ] Update installation instructions
- [ ] Update build instructions
- [ ] Add screenshots of new UI

### 9.5 Release Preparation

- [ ] Bump version in `version.py`
- [ ] Update `CHANGELOG.md` with migration notes
- [ ] Create GitHub release notes
- [ ] Tag release (e.g., `v0.4.0-pyqt6`)

**🎉 Phase 9 Deliverable:** Distributable packages for Windows & Linux

---

## 📋 Phase 10: Deprecation & Cleanup

### 10.1 Archive Old Code

- [ ] Move `FadCrypt.py` → `legacy/FadCrypt_tkinter.py`
- [ ] Move `FadCrypt_Linux.py` → `legacy/FadCrypt_Linux_tkinter.py`
- [ ] Move `ttkbootstrap/` → `legacy/ttkbootstrap/`
- [ ] Keep legacy code for reference during migration

### 10.2 Update Entry Points

- [ ] Rename `FadCrypt_Qt.py` → `FadCrypt.py` (new main entry for Windows)
- [ ] Rename `FadCrypt_Qt_Linux.py` → `FadCrypt_Linux.py` (new main entry for Linux)

### 10.3 CI/CD Updates (if applicable)

- [ ] Update GitHub Actions workflows
- [ ] Update build scripts for PyQt6

### 10.4 Final Verification

- [ ] Test fresh install on clean Windows machine
- [ ] Test fresh install on clean Linux machine
- [ ] Verify all features work identically to Tkinter version

**🎉 Phase 10 Deliverable:** Migration complete! 🎊

---

## 📝 Notes & Conventions

### Code Style

- **OOP:** Use classes for all components (no monolithic functions)
- **DRY:** Extract common logic to `core/` modules
- **Naming:** `snake_case` for methods/vars, `PascalCase` for classes
- **Docstrings:** Google-style docstrings for all classes/methods
- **Comments:** Explain "why", not "what"

### Architecture Patterns

- **Composition over Inheritance:** Inject managers into UI classes
- **Signals/Slots:** Use Qt signals for UI ↔ business logic communication
- **Model-View:** Separate data models from UI (e.g., QListWidget uses model)
- **Single Responsibility:** Each class does ONE thing

### File Organization

```
FadCrypt/
├── core/                   # Business logic (platform-agnostic + specific)
│   ├── base_app_locker.py
│   ├── config_manager.py
│   ├── application_manager.py
│   ├── unified_monitor.py
│   ├── password_manager.py
│   ├── crypto_manager.py
│   ├── autostart_manager.py
│   ├── system_tray_manager.py
│   ├── windows/            # Windows-specific core
│   │   ├── app_locker_windows.py
│   │   ├── registry_manager.py
│   │   └── process_manager.py
│   └── linux/              # Linux-specific core
│       ├── app_locker_linux.py
│       ├── desktop_manager.py
│       └── process_manager.py
├── ui/                     # UI components (PyQt6)
│   ├── base/               # Base/shared UI
│   │   └── main_window_base.py
│   ├── components/         # Reusable widgets
│   │   ├── app_list_widget.py
│   │   ├── button_panel.py
│   │   ├── settings_panel.py
│   │   ├── about_panel.py
│   │   ├── tab_widget.py
│   │   └── system_tray.py
│   ├── dialogs/            # Dialog windows
│   │   ├── password_dialog.py
│   │   ├── change_password_dialog.py
│   │   └── confirm_dialog.py
│   ├── windows/            # Windows-specific UI
│   │   └── main_window_windows.py
│   └── linux/              # Linux-specific UI
│       └── main_window_linux.py
├── FadCrypt.py             # Windows entry point
├── FadCrypt_Linux.py       # Linux entry point
├── version.py              # Centralized versioning
└── requirements.txt        # Dependencies
```

### Migration Checklist (Per Phase)

- [ ] Write docstrings for new classes/methods
- [ ] Add type hints (e.g., `def add_app(self, name: str, path: str) -> bool:`)
- [ ] Test on both Windows & Linux
- [ ] Update documentation if APIs change
- [ ] Commit with descriptive message (e.g., "Phase 3.2: Add password dialog")

---

## 🚀 Getting Started

### Phase 1 First Steps:

1. Install PyQt6: `pip install PyQt6`
2. Create folder structure: `mkdir -p ui/{base,components,dialogs,windows,linux}`
3. Create `FadCrypt_Qt.py` with minimal QApplication + QMainWindow
4. Run: `python FadCrypt_Qt.py` → See empty window ✅

### Current Status: **Phase 0 - Planning Complete** ✅

---

## 📌 Important Reminders

- **No logic loss:** Migrate ALL methods from `AppLocker` and `AppLockerGUI`
- **Test frequently:** Run app after each phase
- **Keep legacy code:** Don't delete Tkinter version until PyQt6 is 100% functional
- **Platform parity:** Windows and Linux must have identical features
- **User data safety:** Don't break existing `~/.FadCrypt/` folder structure

---

**Total Tasks: ~150 | Estimated Time: 2-4 weeks (depending on pace)**

Good luck! 🚀 Let's build a modern, maintainable FadCrypt! 💪
