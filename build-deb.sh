#!/bin/bash
set -e

# Build script for FadCrypt Linux .deb package

echo "=== Building FadCrypt for Linux ==="

# Extract version from version.py
VERSION=$(python3 -c "from version import __version__; print(__version__)")
PACKAGE_NAME=$(python3 -c "from version import PACKAGE_NAME; print(PACKAGE_NAME)")
MAINTAINER=$(python3 -c "from version import MAINTAINER_FULL; print(MAINTAINER_FULL)")
DESCRIPTION=$(python3 -c "from version import PACKAGE_DESCRIPTION; print(PACKAGE_DESCRIPTION)")

# Strip 'v' prefix from version for Debian package (Debian versions must start with a digit)
DEB_VERSION="${VERSION#v}"

echo "Building version: $VERSION (Debian: $DEB_VERSION)"

# Check dependencies
echo "Checking dependencies..."
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 not found"; exit 1; }
command -v pyinstaller >/dev/null 2>&1 || { echo "Error: pyinstaller not found. Install with: pip install pyinstaller"; exit 1; }

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist fadcrypt-deb

# Build with PyInstaller
echo "Building executable with PyInstaller..."
pyinstaller --clean FadCrypt_Linux.spec

# Check if build succeeded
if [ ! -f "dist/fadcrypt" ]; then
    echo "Error: Build failed - executable not found"
    exit 1
fi

# Create .deb package structure
echo "Creating .deb package structure..."
mkdir -p fadcrypt-deb/DEBIAN
mkdir -p fadcrypt-deb/usr/bin
mkdir -p fadcrypt-deb/usr/share/applications
mkdir -p fadcrypt-deb/usr/share/pixmaps
mkdir -p fadcrypt-deb/usr/share/doc/fadcrypt

# Copy files
echo "Copying files..."
cp dist/fadcrypt fadcrypt-deb/usr/bin/
cp debian/fadcrypt.desktop fadcrypt-deb/usr/share/applications/
cp img/1.png fadcrypt-deb/usr/share/pixmaps/fadcrypt.png
cp LICENSE fadcrypt-deb/usr/share/doc/fadcrypt/
cp README.md fadcrypt-deb/usr/share/doc/fadcrypt/

# Set permissions
chmod 755 fadcrypt-deb/usr/bin/fadcrypt
chmod 644 fadcrypt-deb/usr/share/applications/fadcrypt.desktop

# Create control file with dynamic size
INSTALLED_SIZE=$(du -sk fadcrypt-deb/usr | cut -f1)
cat > fadcrypt-deb/DEBIAN/control << EOF
Package: ${PACKAGE_NAME}
Version: ${DEB_VERSION}
Section: utils
Priority: optional
Architecture: amd64
Installed-Size: ${INSTALLED_SIZE}
Depends: python3 (>= 3.8), libgtk-3-0
Maintainer: ${MAINTAINER}
Description: ${DESCRIPTION}
 FadCrypt is a cross-platform GUI application that helps you lock and
 monitor applications with password protection and encrypted configuration.
 .
 Features include:
  - Lock/unlock specific applications
  - Password-protected monitoring
  - System tray integration
  - Auto-start on login support
  - Built-in mini snake game
EOF

# Build the .deb package
echo "Building .deb package..."
dpkg-deb --build fadcrypt-deb ${PACKAGE_NAME}_${DEB_VERSION}_amd64.deb

echo ""
echo "=== Build Complete ==="
echo "Package: ${PACKAGE_NAME}_${DEB_VERSION}_amd64.deb"
echo "App Version: ${VERSION}"
echo ""
echo "To install:"
echo "  sudo dpkg -i ${PACKAGE_NAME}_${DEB_VERSION}_amd64.deb"
echo ""
echo "To run:"
echo "  ${PACKAGE_NAME}"
echo ""
