# FadCrypt Core Modules

This directory contains shared functionality used by both Windows (`FadCrypt.py`) and Linux (`FadCrypt_Linux.py`) versions of FadCrypt.

## Purpose

The `core` module implements the DRY (Don't Repeat Yourself) principle by extracting common functionality into reusable classes that work across both platforms.

## Modules

### `config_manager.py`

Handles configuration import and export operations.

**Features:**

- Export application config to JSON file
- Import config from JSON file with validation
- Automatic backup creation before import
- Platform-independent implementation

**Usage:**

```python
from core.config_manager import ConfigManager

# Initialize
config_mgr = ConfigManager(
    app_locker=your_app_locker_instance,
    get_fadcrypt_folder_func=lambda: your_folder_path
)

# Export
config_mgr.export_config(show_message_func)

# Import
config_mgr.import_config(show_message_func, update_display_func)
```

### `application_manager.py`

Manages the Applications tab, application CRUD operations, statistics, and metadata tracking.

**Features:**

- Complete Applications tab UI with multi-selection support
- Add, edit, remove applications with validation
- Timestamp tracking (added, modified)
- Usage statistics (unlock count, last unlocked)
- Context menu (right-click) with quick actions
- Keyboard shortcuts (Ctrl+A, Delete, Double-click, F2)
- Confirmation dialogs for destructive operations
- Metadata persistence (stored in `app_metadata.json`)
- Icon support with caching (extracts from .desktop files on Linux)

**Usage:**

```python
from core.application_manager import ApplicationManager

# Initialize
app_manager = ApplicationManager(
    app_locker=your_app_locker,
    master=your_tk_window,
    notebook=your_notebook,
    resource_path_func=your_resource_path_function,
    show_message_func=your_message_function,
    update_config_display_func=your_update_function,
    is_linux=True  # or False for Windows
)

# The tab is automatically created
# Methods available:
app_manager.increment_unlock_count(app_name)  # Track unlocks
app_manager.update_apps_listbox()  # Refresh display
```

## Adding New Shared Modules

When adding new features that are identical between Windows and Linux versions:

1. Create a new module in `core/` directory
2. Extract the common functionality into a class or functions
3. Use platform-specific callbacks for UI operations (message boxes, file dialogs, etc.)
4. Import and use the shared module in both `FadCrypt.py` and `FadCrypt_Linux.py`

## Benefits

- ✅ Eliminates code duplication
- ✅ Easier maintenance (fix once, works everywhere)
- ✅ Consistent behavior across platforms
- ✅ Better testability
- ✅ Cleaner codebase structure

## Future Refactoring Candidates

Consider extracting these into core modules:

- Password management (create, change, verify)
- Update checking functionality
- Backup and restore operations
- System monitoring and tray icon management

- Password management (create/change/verify)
- Update checking logic
- Backup/restore functionality
- Common UI components (message dialogs, confirmation dialogs)
- File encryption/decryption utilities
