#!/bin/bash
# Test script for FadCrypt Windows mode on Linux

echo "🧪 Testing FadCrypt with --windows flag"
echo ""
echo "This will run FadCrypt on Linux but simulate Windows environment"
echo "All Windows-specific code (registry, admin checks) will use mocks"
echo ""
echo "Press Ctrl+C to exit when done testing"
echo ""

python3 FadCrypt.py --windows
