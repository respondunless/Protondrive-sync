#!/bin/bash
# Quick launcher script for ProtonDrive Sync

set -e

echo "=================================="
echo "  ProtonDrive Sync Launcher"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "Error: Must be run from the protondrive-sync directory"
    echo "Usage: cd /path/to/protondrive-sync && ./run.sh"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.8 or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version: $PYTHON_VERSION"

# Check if rclone is installed
if ! command -v rclone &> /dev/null; then
    echo "Error: rclone is not installed"
    echo "Please install rclone first:"
    echo "  sudo pacman -S rclone"
    exit 1
fi

echo "✓ Rclone is installed"

# Check for virtual environment
if [ -d "venv" ]; then
    echo "✓ Using virtual environment"
    source venv/bin/activate
else
    echo "ℹ No virtual environment found (optional)"
fi

# Check if PyQt5 is installed
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "⚠ PyQt5 not found, installing dependencies..."
    pip install -r requirements.txt
fi

echo "✓ Dependencies satisfied"
echo ""
echo "Starting ProtonDrive Sync..."
echo "=================================="
echo ""

# Run the application
python3 -m src.main
