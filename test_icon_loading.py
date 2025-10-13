#!/usr/bin/env python3
"""
Test script to verify icon loading logic for FadCrypt applications
"""

import os
import subprocess
from pathlib import Path

def find_desktop_icon(app_path):
    """Find icon from .desktop file"""
    print(f"\n=== Finding desktop icon for: {app_path} ===")
    
    # Get the executable name
    app_name = os.path.basename(app_path).lower()
    print(f"App name: {app_name}")
    
    # Search locations for .desktop files
    desktop_locations = [
        '/usr/share/applications',
        '/usr/local/share/applications',
        os.path.expanduser('~/.local/share/applications')
    ]
    
    for location in desktop_locations:
        if not os.path.exists(location):
            print(f"  Skip: {location} (doesn't exist)")
            continue
            
        print(f"  Checking: {location}")
        
        # Try exact match first
        desktop_file = os.path.join(location, f"{app_name}.desktop")
        if os.path.exists(desktop_file):
            print(f"    ✓ Found: {desktop_file}")
            icon = parse_desktop_file(desktop_file)
            if icon:
                return icon
        
        # Try searching all .desktop files
        try:
            for filename in os.listdir(location):
                if not filename.endswith('.desktop'):
                    continue
                    
                if app_name in filename.lower():
                    desktop_file = os.path.join(location, filename)
                    print(f"    ~ Partial match: {desktop_file}")
                    icon = parse_desktop_file(desktop_file)
                    if icon:
                        return icon
        except Exception as e:
            print(f"    ✗ Error reading {location}: {e}")
    
    print(f"  ✗ No .desktop file found")
    return None

def parse_desktop_file(desktop_file):
    """Parse .desktop file to extract icon"""
    print(f"      Parsing: {desktop_file}")
    try:
        with open(desktop_file, 'r') as f:
            for line in f:
                if line.startswith('Icon='):
                    icon = line.split('=', 1)[1].strip()
                    print(f"        Icon entry: {icon}")
                    return icon
    except Exception as e:
        print(f"        ✗ Error parsing: {e}")
    return None

def find_icon_by_name(icon_name):
    """Search for icon file in standard directories"""
    print(f"\n=== Finding icon file for: {icon_name} ===")
    
    icon_dirs = [
        '/usr/share/pixmaps',
        '/usr/share/icons/hicolor/48x48/apps',
        '/usr/share/icons/hicolor/32x32/apps',
        '/usr/share/icons/hicolor/256x256/apps',
        '/usr/share/icons/hicolor/scalable/apps',
        '/usr/share/app-install/icons',
    ]
    
    extensions = ['.png', '.svg', '.xpm']
    name_variants = [icon_name.lower(), icon_name.capitalize(), icon_name]
    
    for icon_dir in icon_dirs:
        if not os.path.exists(icon_dir):
            print(f"  Skip: {icon_dir} (doesn't exist)")
            continue
            
        print(f"  Checking: {icon_dir}")
        
        for name_variant in name_variants:
            for ext in extensions:
                icon_path = os.path.join(icon_dir, f"{name_variant}{ext}")
                if os.path.exists(icon_path):
                    print(f"    ✓ FOUND: {icon_path}")
                    return icon_path
    
    print(f"  ✗ Icon file not found")
    return None

def test_icon_for_app(app_path):
    """Test complete icon loading for an application"""
    print(f"\n{'='*70}")
    print(f"TESTING: {app_path}")
    print(f"{'='*70}")
    
    # Check if app exists
    if not os.path.exists(app_path):
        print(f"  ✗ Application does not exist!")
        return None
    
    print(f"  ✓ Application exists")
    
    # Step 1: Find icon name from .desktop file
    icon_name = find_desktop_icon(app_path)
    
    if not icon_name:
        print(f"\n  → No icon name found from .desktop file")
        # Try using app name as fallback
        icon_name = os.path.basename(app_path).lower()
        print(f"  → Using app basename as fallback: {icon_name}")
    
    # Step 2: Check if icon_name is already a full path
    if icon_name.startswith('/') and os.path.exists(icon_name):
        print(f"\n  ✓ Icon is full path and exists: {icon_name}")
        return icon_name
    
    # Step 3: Find actual icon file
    icon_path = find_icon_by_name(icon_name)
    
    if icon_path:
        print(f"\n  ✓ SUCCESS: Icon found at {icon_path}")
        return icon_path
    else:
        print(f"\n  ✗ FAILED: No icon file found")
        return None

# Test with actual applications
test_apps = [
    '/usr/bin/brave-browser',
    '/usr/bin/google-chrome',
    '/usr/bin/firefox',
]

print("=" * 70)
print("FADCRYPT ICON LOADING TEST")
print("=" * 70)

results = {}
for app_path in test_apps:
    icon_path = test_icon_for_app(app_path)
    results[app_path] = icon_path

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

for app_path, icon_path in results.items():
    app_name = os.path.basename(app_path)
    if icon_path:
        print(f"  ✓ {app_name:20s} → {icon_path}")
    else:
        print(f"  ✗ {app_name:20s} → NO ICON FOUND")

print("=" * 70)
