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

- Password management (create/change/verify)
- Update checking logic
- Backup/restore functionality
- Common UI components (message dialogs, confirmation dialogs)
- File encryption/decryption utilities
