"""
FadCrypt Windows Module
Provides Windows-specific functionality and privilege elevation.

This module includes:
- WindowsElevationManager: Professional privilege escalation via Task Scheduler
- Helper script: Elevated operations handler
"""

from .elevation_manager import WindowsElevationManager, get_elevation_manager

__all__ = [
    'WindowsElevationManager',
    'get_elevation_manager',
]
