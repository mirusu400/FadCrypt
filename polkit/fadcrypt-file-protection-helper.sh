#!/bin/bash
#
# FadCrypt File Protection Helper
# This script is executed via pkexec with polkit authorization
# to set immutable flags on critical files.
#

set -e

ACTION="$1"
shift

if [ "$ACTION" = "protect" ]; then
    # Set immutable flag on all provided files
    for file in "$@"; do
        if [ -f "$file" ]; then
            chattr +i "$file" 2>/dev/null || chmod 400 "$file"
            echo "Protected: $file"
        fi
    done
elif [ "$ACTION" = "unprotect" ]; then
    # Remove immutable flag from all provided files
    for file in "$@"; do
        if [ -f "$file" ]; then
            chattr -i "$file" 2>/dev/null || chmod 644 "$file"
            echo "Unprotected: $file"
        fi
    done
else
    echo "Usage: $0 {protect|unprotect} <files...>"
    exit 1
fi

exit 0
