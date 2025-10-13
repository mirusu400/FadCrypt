# FadCrypt PyQt6 Migration - Progress Tracker

**Last Updated:** 2025-10-13  
**Current Phase:** 5 - Platform Architecture (80% Complete)  
**Next Phase:** 6 - Autostart & State Persistence

## 🎉 Recent Accomplishments (This Session)

- ✅ **Password Dialog Redesign** - Modern 480x280px design with proper padding and wrapping
- ✅ **Threading Fix** - Qt signal/slot pattern for thread-safe password dialogs (CRITICAL BUG FIX)
- ✅ **Platform Architecture** - Created MainWindowLinux and MainWindowWindows with inheritance
- ✅ **Platform Detection** - Entry point now detects OS and loads appropriate class
- ✅ **Autostart Implementation** - Linux .desktop and Windows registry methods complete
- ✅ **System Tray** - QSystemTrayIcon with context menu and notifications
- ✅ **UnifiedMonitor** - Integrated with callbacks and monitoring lifecycle
- ✅ **Applications Grid UI** - Card-based grid with icons from .desktop files
- ✅ **Config Tab Live Display** - Real-time updates when apps added/removed

## 🎯 Architecture Goals

- Migrate from Tkinter to PyQt6 for modern, cross-platform UI ✅
- Refactor monolithic files into clean OOP architecture ✅
- Maintain ALL existing functionality and logic ✅
- Use DRY principle: shared business logic in `core/`, UI in `ui/` ✅
- Platform-specific code via inheritance (MainWindowBase → Linux/Windows) ✅
- No loss of context, features, or mechanisms ✅

---

## ✅ Phase 1: Foundation (COMPLETE - 100%)

- ✅ Project structure with ui/ and core/ separation
- ✅ PyQt6 6.9.0 installed and working
- ✅ Core managers created (CryptoManager, PasswordManager, AutostartManager)
- ✅ Version management using version.py (**version**, **version_code**)
- ✅ Resource path handling for PyInstaller (resource_path method)
- ✅ Custom Ubuntu font integration (core/fonts/ubuntu_regular.ttf)

## ✅ Phase 2: Core UI Widgets (COMPLETE - 100%)

- ✅ MainWindowBase with all 5 tabs (Main, Applications, Config, Settings, About)
- ✅ Complete UI parity with Tkinter:
  - ✅ Main tab: Banner image, centered buttons, sidebar, footer with logo/branding
  - ✅ Applications tab: **NEW** Grid layout with app cards and icons (IMPROVED from Tkinter)
  - ✅ Config tab: Live config display with real-time updates
  - ✅ Settings tab: Dialog style selector, wallpaper preview, system tools checkbox
  - ✅ About tab: FadCam promotion with image, FadSec Lab info, all social buttons
- ✅ AppGridWidget (350 lines) - Card-based grid with icons, selection, drag-drop
- ✅ ButtonPanel (80 lines) - Add/Remove/Select All/Deselect All actions
- ✅ SettingsPanel (280 lines) - Radio buttons, preview sections, detailed descriptions
- ✅ AboutPanel (300 lines) - Update checker, FadCam promo, external links
- ✅ Password dialogs (PasswordDialog, ChangePasswordDialog - modern redesign)
- ✅ Add Application Dialog (350 lines) - Drag-drop, browse, scan apps, modern styling
- ✅ Snake game extracted to core/snake_game.py with threading
- ✅ All helper texts and descriptions match Tkinter exactly

## ✅ Phase 3: Business Logic Integration (COMPLETE - 100%)

- ✅ Entry point working with version.py
- ✅ Custom font loading application-wide (Ubuntu Regular from core/fonts/)
- ✅ Snake game handler connected
- ✅ Password create/change workflows fully working
- ✅ Application add/remove functionality with grid UI
- ✅ Config save/load from JSON with live display updates
- ✅ Settings save/load from JSON
- ✅ System tray integration with QSystemTrayIcon
- ✅ UnifiedMonitor integrated with password prompts
- ✅ Threading fix for Qt widgets from monitoring thread

## 🔄 Phase 4: Monitoring Integration (90% COMPLETE - NEARLY DONE)

- ✅ System tray integration (QSystemTrayIcon)
  - ✅ Created system tray icon with context menu
  - ✅ Added Show/Hide, Start/Stop Monitoring, Exit actions
  - ✅ Minimize to tray on monitoring start
  - ✅ Tray icon updates based on monitoring status
- ✅ Integrate UnifiedMonitor with UI state
  - ✅ Initialize UnifiedMonitor with callbacks
  - ✅ Pass application list from grid
  - ✅ Start/stop monitoring lifecycle
  - ✅ Logging output to console
- ✅ Password prompts during monitoring
  - ✅ Show password dialog when blocked app launches (thread-safe)
  - ✅ Integrated with UnifiedMonitor callbacks
  - ✅ Unlock app on correct password entry
  - ✅ Track unlock count in config
  - ✅ Fixed Qt threading violations with pyqtSignal
- ✅ Password dialog modern redesign
  - ✅ Better sizing: 480x280px (was 400x250)
  - ✅ Proper padding: 35px margins, 18px spacing
  - ✅ Refined input: 48px height, proper focus states
  - ✅ Modern buttons: Unlock (green) and Cancel (gray)
  - ✅ Centered text with proper wrapping (max-width 410px)
- ⏳ Testing
  - [ ] Verify monitoring blocks apps correctly
  - [ ] Test password prompt appears without threading errors
  - [ ] Test unlock functionality and state persistence
- [ ] Error handling and user feedback
- [ ] Linux testing (Ubuntu, Arch, Fedora)
- ⏳ Testing
  - [ ] Verify monitoring blocks apps correctly
  - [ ] Test password prompt appears without threading errors
  - [ ] Test unlock functionality and state persistence

## ⏳ Phase 5: Platform Architecture (TODO - 0%)

- [ ] Create ui/windows/main_window_windows.py extending MainWindowBase
- [ ] Create ui/linux/main_window_linux.py extending MainWindowBase
- [ ] Implement platform detection in entry points (FadCrypt_Qt.py)
- [ ] Move Windows-specific logic (winreg, ctypes) to Windows class
- [ ] Move Linux-specific logic (fcntl, .desktop) to Linux class
- [ ] Test inheritance pattern with shared MainWindowBase functionality

## ⏳ Phase 6: Autostart & State Persistence (TODO - 0%)

- [ ] Linux autostart: Create .desktop file in ~/.config/autostart/
- [ ] Windows autostart: Registry entry or Startup folder
- [ ] Add autostart checkbox in Settings tab
- [ ] Save/restore unlocked apps state to JSON
- [ ] Persist monitoring state across restarts
- [ ] Test autostart on both platforms

## ⏳ Phase 7: Polish & Testing (TODO - 0%)

- [ ] End-to-end testing on Linux (Ubuntu, Arch, Fedora)
- [ ] Windows testing (10/11)
- [ ] PyInstaller packaging test (.spec file updates for PyQt6)
- [ ] Performance testing (CPU/memory usage during monitoring)
- [ ] System tools locking (terminals, monitors) - Linux only
- [ ] Cleanup on uninstall functionality
- [ ] File monitoring and automatic backups
- [ ] Error handling and user feedback improvements

---

## 📝 Legacy Sections (Pre-Session Context - Keep for Reference)

## 🎯 Goals

- [x] Project structure with ui/ and core/ separation

- [x] PyQt6 6.9.0 installed- ✅ Project structure with ui/ and core/ separation

- [x] Core managers (CryptoManager, PasswordManager, AutostartManager, ConfigManager, ApplicationManager)

- [x] Version management from version.py- ✅ PyQt6 6.9.0 installed and working- Migrate from Tkinter to PyQt6 for modern, cross-platform UI

- [x] Resource path handling for PyInstaller

- [x] Custom Ubuntu font integration (core/fonts/ubuntu_regular.ttf)- ✅ Core managers created (CryptoManager, PasswordManager, AutostartManager)- Refactor monolithic files into clean OOP architecture

## Phase 2: Core UI Widgets- ✅ Version management using version.py (**version**, **version_code**)- Maintain ALL existing functionality and logic

- [x] MainWindowBase with all 5 tabs

- [x] AppListWidget with drag-drop and context menus- ✅ Resource path handling for PyInstaller (resource_path method)- Use DRY principle: shared business logic in `core/`, UI in `ui/`

- [x] ButtonPanel for actions

- [x] SettingsPanel with preview sections- ✅ Custom Ubuntu font integration (core/fonts/ubuntu_regular.ttf)- Platform-specific code via inheritance (Windows base → Linux extends)

- [x] AboutPanel with FadCam promotion

- [x] Password dialogs (PasswordDialog, ChangePasswordDialog)- No loss of context, features, or mechanisms

- [x] Snake game extracted to core/snake_game.py

- [ ] Improve home tab design (modern, not 1:1 Tkinter clone)## ✅ Phase 2: Core UI Widgets (COMPLETE)

- [ ] Fix preview images in Settings tab

- [ ] Fix readme button to show fullscreen dialog (not browser)- ✅ MainWindowBase with all 5 tabs (Main, Applications, Config, Settings, About)---

## Phase 3: Business Logic Integration- ✅ Complete UI parity with Tkinter:

- [x] Entry point working with version.py

- [x] Custom font loading - ✅ Main tab: Banner image, centered buttons, sidebar, footer with logo/branding## 📋 Phase 1: Foundation & Basic Setup (First Working Prototype)

- [x] Snake game handler connected

- [ ] Connect button handlers to core managers - ✅ Applications tab: App list, drag-drop, lock/unlock, context menus

- [ ] Integrate CryptoManager for encryption/decryption

- [ ] Integrate PasswordManager for password workflows - ✅ Config tab: Encrypted apps display, export/import functionality### 1.1 Project Structure Setup ✅

- [ ] Integrate ConfigManager for app list persistence

- [ ] Application add/remove/lock/unlock functionality - ✅ Settings tab: Dialog style selector, wallpaper preview, system tools checkbox

- [ ] Config import/export with file dialogs

- [ ] Settings save/load from JSON - ✅ About tab: FadCam promotion with image, FadSec Lab info, all social buttons- [x] Create `ui/` folder for all UI components

- [ ] Create password workflow

- [ ] Change password workflow- ✅ AppListWidget (260 lines) - Full drag-drop, context menu, tooltips- [x] Create `ui/__init__.py` with package exports

- [ ] Fullscreen password dialog implementation

- [ ] Simple password dialog implementation- ✅ ButtonPanel (80 lines) - Add/Remove/Edit actions- [x] Create `ui/base/` for base/shared UI components

## Phase 4: Monitoring Integration- ✅ SettingsPanel (280 lines) - Radio buttons, preview sections, detailed descriptions- [x] Create `ui/windows/` for Windows-specific UI

- [ ] Integrate UnifiedMonitor with UI state

- [ ] Password prompts during monitoring- ✅ AboutPanel (300 lines) - Update checker, FadCam promo, external links- [x] Create `ui/linux/` for Linux-specific UI

- [ ] System tray integration (QSystemTrayIcon)

- [ ] Process blocking implementation- ✅ Password dialogs (PasswordDialog, ChangePasswordDialog - 260 lines)- [x] Create `ui/components/` for reusable widgets

- [ ] Auto-start functionality

- [ ] State persistence during monitoring- ✅ Snake game extracted to core/snake_game.py with threading- [x] Create `ui/dialogs/` for dialog windows

## Phase 5: Polish & Testing- ✅ All helper texts and descriptions match Tkinter exactly- [ ] Update `.gitignore` for PyQt6 cache files

- [ ] Settings persistence across restarts

- [ ] System tools locking (terminals, monitors)## 🔄 Phase 3: Business Logic Integration (40% - IN PROGRESS)### 1.2 Dependencies & Environment ✅

- [ ] Cleanup on uninstall functionality

- [ ] File monitoring and automatic backups- ✅ Entry point fixed (FadCrypt_Qt.py - no app_name parameter)

- [ ] Error handling and user feedback

- [ ] Linux testing (Ubuntu, Arch, Fedora)- ✅ Version from version.py (**version** = "v0.3.0", **version_code** = 3)- [x] Add PyQt6 to `requirements.txt` (PyQt6, PyQt6-Qt6, PyQt6-sip)

- [ ] PyInstaller packaging test

- [ ] Windows testing- ✅ Custom font loading application-wide (Ubuntu Regular from core/fonts/)- [ ] Create `requirements-dev.txt` for development tools

- [ ] Documentation updates

- ✅ Snake game handler connected (on_snake_game calls core.snake_game.start_snake_game)- [x] Test PyQt6 installation on Windows & Linux

- ✅ All UI components created and styled with proper layouts- [ ] Document Qt Designer usage (optional)

- ⏳ NEXT: Connect button handlers to core managers

- ⏳ Integrate CryptoManager for encryption/decryption### 1.3 Core Business Logic Extraction (Platform-Agnostic) ✅

- ⏳ Integrate PasswordManager for password workflows

- ⏳ Integrate ConfigManager for app list persistence- [x] Move encryption/decryption logic from `AppLocker` to `core/crypto_manager.py`

- ⏳ Application add/remove/lock/unlock functionality- [x] Move password management to `core/password_manager.py`

- ⏳ Config import/export with file dialogs- [ ] Extend `core/config_manager.py` with all config operations

- ⏳ Settings save/load from JSON- [ ] Extend `core/application_manager.py` with platform-agnostic app logic

- [x] Keep `core/unified_monitor.py` as-is (already platform-agnostic)

## ⏳ Phase 4: Monitoring Integration (TODO)- [x] Create `core/autostart_manager.py` for startup logic (platform-specific methods)

- [ ] Integrate UnifiedMonitor with UI state- [ ] Create `core/system_tray_manager.py` for tray icon logic

- [ ] Password prompts during monitoring (fullscreen/simple dialog)

- [ ] System tray integration (pystray → QSystemTrayIcon)### 1.4 Platform-Specific Business Logic Separation (SKIP FOR NOW)

- [ ] Process blocking implementation

- [ ] Auto-start functionality (Linux .desktop, Windows registry)- [ ] Create `core/windows/registry_manager.py` (winreg operations) - DEFERRED

- [ ] State persistence during monitoring sessions- [ ] Create `core/windows/process_manager.py` (Windows process handling) - DEFERRED

- [ ] Create `core/linux/desktop_manager.py` (.desktop file operations) - DEFERRED

## ⏳ Phase 5: Polish & Testing (TODO)- [ ] Create `core/linux/process_manager.py` (Linux process handling, fcntl locks) - DEFERRED

- [ ] Settings persistence across restarts

- [ ] Password create/change workflows fully working### 1.5 Create Base AppLocker Class (Platform-Agnostic) - DEFERRED TO PHASE 6

- [ ] System tools locking (terminals, monitors)

- [ ] Cleanup on uninstall functionality- [ ] Create `core/base_app_locker.py` with shared methods

- [ ] File monitoring and automatic backups- [ ] Extract methods: `get_fadcrypt_folder()`, `resource_path()`, etc.

- [ ] Comprehensive error handling- [ ] Extract: password validation, app add/remove/edit logic

- [ ] Linux testing (Ubuntu, Arch, Fedora)- [ ] Extract: config save/load operations (use ConfigManager)

- [ ] PyInstaller packaging and distribution testing- [ ] Use composition: inject platform-specific managers

---### 1.6 Basic PyQt6 Main Window ✅

## 📝 Recent Fixes (Current Session)- [x] Create `ui/base/main_window_base.py` with QMainWindow

- [x] Set window properties: title, icon, size (700x650)

### Issues Fixed- [x] Add menu bar stub

1. ✅ **TypeError in FadCrypt_Qt.py** - Removed `app_name` parameter from MainWindowBase- [x] Add central widget with QTabWidget placeholder

2. ✅ **Version hardcoding** - Now uses **version** and **version_code** from version.py- [x] Add status bar

3. ✅ **Custom font not loaded** - Added load_custom_font() method with QFontDatabase

4. ✅ **Snake game not modular** - Extracted to core/snake_game.py with proper gui_instance handling### 1.7 Basic Entry Point ✅

5. ✅ **AboutPanel signature mismatch** - Fixed to accept (version, version_code, resource_path_func)

- [x] Create `FadCrypt_Qt.py` (new entry point for testing)

### Current State- [x] Import PyQt6 (QApplication, QMainWindow)

- Entry point works: `python3 FadCrypt_Qt.py` launches successfully- [x] Initialize QApplication

- All tabs render with proper content and styling- [x] Load base main window

- Custom Ubuntu font applies to entire application- [ ] Add command-line arg parsing (`--auto-monitor`, etc.)

- Snake game can be launched from Snake Game button- [x] Test: Launch app and see empty window

- Images load via resource_path() method

- Version displayed correctly in About tab**🎉 Phase 1 Deliverable:** Empty PyQt6 window launches successfully

---

## 🎯 Next Immediate Steps## 📋 Phase 2: Core UI Widgets & Layout

### 1. Test Current Build### 2.1 Main Tab Structure ✅

````bash

cd /mnt/linux2/repos/FadCrypt- [x] Create `ui/components/tab_widget.py` (custom QTabWidget) - using built-in

python3 FadCrypt_Qt.py- [x] Add "Home" tab (QWidget)

```- [x] Add "Settings" tab (QWidget)

- Verify all tabs load- [x] Add "About" tab (QWidget)

- Check if images display (banner, logos, FadCam icon)- [ ] Style tabs (match dark theme from Tkinter version)

- Test if snake game button works

- Verify custom font is applied### 2.2 Home Tab - Application List ✅



### 2. Connect Core Managers (Phase 3 Completion)- [x] Create `ui/components/app_list_widget.py` (QListWidget or QTreeWidget)

Create `ui/managers/` directory with PyQt6 signal wrappers:- [x] Design list item: app name, path, status (locked/unlocked)

- `app_manager_qt.py` - Wrap ApplicationManager with signals- [ ] Add custom item delegate for styled rendering

- `password_manager_qt.py` - Wrap PasswordManager with signals- [x] Add context menu (right-click): Edit, Remove, Open Location

- `config_manager_qt.py` - Wrap ConfigManager with signals- [x] Add drag-and-drop support (QListWidget.setAcceptDrops)



### 3. Implement Button Handlers### 2.3 Home Tab - Control Buttons ✅

Connect UI events to business logic:

- `on_start_monitoring()` → Create app_locker, start UnifiedMonitor- [x] Create `ui/components/button_panel.py` (QWidget with QHBoxLayout)

- `on_stop_monitoring()` → Stop monitor, re-enable tools- [x] Add buttons: Add Application, Lock All, Unlock All

- `on_create_password()` → Show PasswordDialog, call PasswordManager- [x] Connect button signals to slots (stub methods)

- `on_change_password()` → Show ChangePasswordDialog, call PasswordManager- [ ] Style buttons (match existing theme)

- `on_export_config()` → File dialog, call ConfigManager.export_config()

- `on_import_config()` → File dialog, call ConfigManager.import_config()- [ ] Create `ui/components/button_panel.py` (QWidget with QHBoxLayout)

- [ ] Add buttons: Add Application, Lock All, Unlock All

### 4. Wire Up App List- [ ] Connect button signals to slots (stub methods)

- Connect AppListWidget signals to ApplicationManager- [ ] Style buttons (match existing theme)

- Implement add_application with file browser + drag-drop

- Implement remove_application with confirmation### 2.4 Settings Tab - Basic Layout ✅

- Implement lock/unlock toggle with icon updates

- [x] Create `ui/components/settings_panel.py` (QWidget)

---- [x] Add QFormLayout for settings

- [x] Add QCheckBox: "Lock System Tools"

## 📊 Code Metrics- [x] Add QComboBox: "Password Dialog Style" (simple/fullscreen)

- [x] Add QComboBox: "Wallpaper Choice" (default/custom)

| Component | Lines | Status | Notes |- [x] Add QPushButton: "Change Master Password"

|-----------|-------|--------|-------|

| **Entry Point** | | | |### 2.5 About Tab ✅

| FadCrypt_Qt.py | 60 | ✅ | Fixed, uses version.py |

| **Core Managers** | | | |- [x] Create `ui/components/about_panel.py` (QWidget)

| crypto_manager.py | 250 | ✅ | AES-256-GCM, PBKDF2-HMAC-SHA256 |- [x] Display app version, version code

| password_manager.py | 160 | ✅ | Create, verify, change password |- [x] Display credits, GitHub link (QLabel with hyperlinks)

| autostart_manager.py | 300 | ✅ | Linux .desktop, Windows registry |- [ ] Add FadCrypt logo (QLabel with QPixmap)

| config_manager.py | 180 | ✅ | JSON persistence |

| application_manager.py | 250 | ✅ | App list operations |**🎉 Phase 2 Deliverable:** All tabs visible with UI elements (non-functional) - DONE ✅

| unified_monitor.py | 450 | ✅ | CPU-optimized monitoring |

| snake_game.py | 540 | ✅ | Extracted, threaded |---

| **UI Components** | | | |

| main_window_base.py | 480 | ✅ | All 5 tabs, custom font |## 📋 Phase 3: Connect UI to Business Logic

| app_list_widget.py | 260 | ✅ | Drag-drop, context menus |

| button_panel.py | 80 | ✅ | Action buttons |### 3.1 Initialize Core Managers in Main Window - DEFERRED

| settings_panel.py | 280 | ✅ | Previews, descriptions |

| about_panel.py | 300 | ✅ | FadCam promo, links |- [ ] Instantiate `ConfigManager` in main window

| password_dialog.py | 260 | ✅ | Input dialogs |- [ ] Instantiate `ApplicationManager`

| **TOTAL** | ~3,600 | 60% | UI done, logic pending |- [ ] Instantiate `UnifiedMonitor`

- [ ] Instantiate `PasswordManager`

---- [ ] Instantiate `CryptoManager`

- [ ] Pass managers to UI components via constructor

## 🐛 Known Issues

### 3.2 Password Dialog (PyQt6) ✅

### Non-Critical (Linting)

- ⚠️ PyLint warnings about PyQt6 dynamic attributes (can ignore)- [x] Create `ui/dialogs/password_dialog.py` (QDialog)

- ⚠️ Snake game has pygame dynamic attribute warnings (can ignore)- [x] Simple version: QLabel + QLineEdit (password) + OK/Cancel buttons

- ⚠️ Type checking errors for Qt types (PyQt6 uses runtime types)- [ ] Fullscreen version: full-screen QDialog with wallpaper background

- [ ] Add rounded corners styling (QSS stylesheet)

### Critical (Blockers)- [ ] Connect to `PasswordManager.verify_password()`

- ❌ **No app_locker instance** - MainWindowBase needs AppLocker reference

- ❌ **Managers not connected** - UI buttons don't call business logic yet### 3.3 Add Application Functionality ✅

- ❌ **Settings not persisted** - Changes lost on restart

- ❌ **Images not tested** - Need to verify img/ folder assets load correctly- [x] Connect "Add Application" button to slot

- [x] Show QFileDialog to select executable

---- [x] On Linux: filter for executables or .desktop files

- [ ] On Windows: filter for .exe files

## 🧪 Testing Commands- [x] Call `ApplicationManager.add_application()` - READY

- [x] Refresh app list widget

### Quick Smoke Test

```bash### 3.4 Remove/Edit Application ✅

# Launch app

python3 FadCrypt_Qt.py- [x] Connect context menu "Remove" to slot

- [x] Show confirmation dialog (QMessageBox)

# Should see:- [x] Call `ApplicationManager.remove_application()` - READY

# ✅ FadCrypt v0.3.0 started successfully!- [x] Connect context menu "Edit" to slot

# 🔢 Version Code: 3- [ ] Show edit dialog (QInputDialog or custom dialog)

# 🎨 UI Framework: PyQt6

# ✅ Loaded custom font: Ubuntu### 3.5 Lock/Unlock All Applications ✅

````

- [x] Connect "Lock All" button to slot

### Manual Testing Checklist- [x] Call `ApplicationManager.lock_all_applications()` - READY

- [ ] Main tab displays banner image- [x] Update UI (lock icons/status)

- [ ] Footer shows FadSec logo and branding- [x] Connect "Unlock All" button to slot

- [ ] Applications tab has app list widget- [ ] Prompt for master password via `PasswordDialog`

- [ ] Config tab shows encrypted apps text area- [x] Call `ApplicationManager.unlock_all_applications()` - READY

- [ ] Settings tab has preview section

- [ ] About tab shows FadCam icon and promo### 3.6 Individual App Lock/Unlock ✅

- [ ] Snake Game button launches pygame window

- [ ] All text uses Ubuntu font- [x] Add toggle button/checkbox in app list items

- [ ] Window icon displays correctly- [x] Connect toggle to slot

- [x] Call `ApplicationManager.lock_application(app_name)` - READY

---- [x] Call `ApplicationManager.unlock_application(app_name)` - READY

## 🎨 UI Architecture**🎉 Phase 3 Deliverable:** Can add/remove apps, lock/unlock functionality works - 70% DONE

````---

MainWindowBase (QMainWindow)

├── MenuBar (File, Help)## 📋 Phase 4: Application Monitoring Integration

├── QTabWidget

│   ├── Main Tab### 4.1 Connect UnifiedMonitor to UI

│   │   ├── Banner Image (QLabel with QPixmap)

│   │   ├── Centered Buttons (Start, Read Me)- [ ] Start `UnifiedMonitor` when monitoring is enabled

│   │   ├── Sidebar Buttons (Stop, Create/Change Pass, Snake)- [ ] Connect monitor signals to UI slots (for status updates)

│   │   └── Footer (Logo, Branding, GitHub link)- [ ] Add "Start Monitoring" / "Stop Monitoring" button

│   ├── Applications Tab- [ ] Show monitoring status in status bar (e.g., "Monitoring: 5 apps")

│   │   ├── AppListWidget (drag-drop, context menu)

│   │   └── ButtonPanel (Add, Remove, Edit)### 4.2 Password Prompt on App Launch

│   ├── Config Tab (QScrollArea)

│   │   ├── Config Text Display (QTextEdit)- [ ] `UnifiedMonitor` detects locked app launch

│   │   └── Export/Import Buttons- [ ] Emit signal to main window

│   ├── Settings Tab (QScrollArea)- [ ] Main window shows `PasswordDialog`

│   │   ├── Dialog Style Radio Buttons- [ ] On correct password: unlock app and let it run

│   │   ├── Wallpaper Selection- [ ] On incorrect password: terminate process (Linux: `proc.terminate()`)

│   │   ├── Preview Section

│   │   ├── System Tools Checkbox### 4.3 System Tray Integration

│   │   └── File Locations Info

│   └── About Tab (QScrollArea)- [ ] Create `ui/components/system_tray.py` (QSystemTrayIcon)

│       ├── App Icon + Version- [ ] Add tray icon (use existing icon from `img/`)

│       ├── Update Button- [ ] Add tray menu: Show, Hide, Start Monitoring, Stop Monitoring, Exit

│       ├── FadSec Suite Description- [ ] Connect menu actions to main window methods

│       ├── Action Buttons (Source, Coffee, Discord, Review)- [ ] Implement minimize-to-tray behavior

│       └── FadCam Promotion Section

```### 4.4 Autostart on Boot



---- [ ] Use `core/autostart_manager.py` methods

- [ ] Add checkbox in Settings: "Start with System"

## 🔧 Environment Setup- [ ] On Windows: create registry entry or shortcut in Startup folder

- [ ] On Linux: create `.desktop` file in `~/.config/autostart/`

### Dependencies- [ ] Test: reboot and verify FadCrypt starts in tray

```bash

pip install PyQt6 cryptography psutil pystray pygame requests**🎉 Phase 4 Deliverable:** Full monitoring workflow functional

````

---

### Font Installation

- Custom font located at: `core/fonts/ubuntu_regular.ttf`## 📋 Phase 5: Settings & Persistence

- Loaded via QFontDatabase.addApplicationFont()

- Applied application-wide via QApplication.setFont()### 5.1 Settings Save/Load

### Running- [ ] Connect all settings widgets to slots

```bash- [ ] On change: save to `settings.json`via`ConfigManager`

# Development- [ ] On app launch: load settings and populate widgets

python3 FadCrypt_Qt.py- [ ] Apply settings: dialog style, wallpaper, lock tools, etc.

# Production (TODO)### 5.2 Master Password Management

pyinstaller FadCrypt.spec

```- [ ] "Change Master Password" button → show dialog

- [ ] Create `ui/dialogs/change_password_dialog.py`

---- [ ] Old password + New password + Confirm new password

- [ ] Call `PasswordManager.change_password()`

## 📚 Architecture Decisions- [ ] Re-encrypt all app passwords with new master password



1. **Single Version Source** - version.py contains __version__ and __version_code__### 5.3 Lock System Tools (Linux)

2. **Custom Font Everywhere** - Ubuntu Regular for consistent branding

3. **Resource Path Method** - Supports both dev and PyInstaller bundled assets- [ ] Connect "Lock System Tools" checkbox to slot

4. **Snake Game Module** - Extracted to core/ for reusability and cleaner code- [ ] Use existing logic from `FadCrypt_Linux.py` (lines 2700-2800)

5. **Signal-Slot Pattern** - PyQt6 signals for UI-logic communication (TODO)- [ ] Disable execute permissions on system tools (`chmod -x`)

6. **Manager Wrappers** - PyQt6-specific wrappers around core managers (TODO)- [ ] Store disabled tools in `disabled_tools.txt`

- [ ] Add "Unlock Tools" cleanup logic

---

### 5.4 Custom Wallpaper Selection

Last Updated: Current Session

Phase: 3/5 (Business Logic Integration)- [ ] "Wallpaper Choice" combobox → add "Browse..." option

Progress: 60% Complete- [ ] Show QFileDialog to select image

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
├── core/ # Business logic (platform-agnostic + specific)
│ ├── base_app_locker.py
│ ├── config_manager.py
│ ├── application_manager.py
│ ├── unified_monitor.py
│ ├── password_manager.py
│ ├── crypto_manager.py
│ ├── autostart_manager.py
│ ├── system_tray_manager.py
│ ├── windows/ # Windows-specific core
│ │ ├── app_locker_windows.py
│ │ ├── registry_manager.py
│ │ └── process_manager.py
│ └── linux/ # Linux-specific core
│ ├── app_locker_linux.py
│ ├── desktop_manager.py
│ └── process_manager.py
├── ui/ # UI components (PyQt6)
│ ├── base/ # Base/shared UI
│ │ └── main_window_base.py
│ ├── components/ # Reusable widgets
│ │ ├── app_list_widget.py
│ │ ├── button_panel.py
│ │ ├── settings_panel.py
│ │ ├── about_panel.py
│ │ ├── tab_widget.py
│ │ └── system_tray.py
│ ├── dialogs/ # Dialog windows
│ │ ├── password_dialog.py
│ │ ├── change_password_dialog.py
│ │ └── confirm_dialog.py
│ ├── windows/ # Windows-specific UI
│ │ └── main_window_windows.py
│ └── linux/ # Linux-specific UI
│ └── main_window_linux.py
├── FadCrypt.py # Windows entry point
├── FadCrypt_Linux.py # Linux entry point
├── version.py # Centralized versioning
└── requirements.txt # Dependencies

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
```
