#!/bin/bash
# Verification script for ProtonDrive Sync setup

echo "======================================"
echo "  ProtonDrive Sync - Setup Verification"
echo "======================================"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

# Check 1: Python version
echo -n "Checking Python version... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
        echo "✓ PASS (Python $PYTHON_VERSION)"
        ((CHECKS_PASSED++))
    else
        echo "✗ FAIL (Python $PYTHON_VERSION is too old, need 3.8+)"
        ((CHECKS_FAILED++))
    fi
else
    echo "✗ FAIL (Python 3 not found)"
    ((CHECKS_FAILED++))
fi

# Check 2: Rclone installation
echo -n "Checking rclone installation... "
if command -v rclone &> /dev/null; then
    RCLONE_VERSION=$(rclone version 2>&1 | head -n1 | grep -oP 'v[\d.]+')
    echo "✓ PASS (rclone $RCLONE_VERSION)"
    ((CHECKS_PASSED++))
else
    echo "✗ FAIL (rclone not found)"
    echo "  Install with: sudo pacman -S rclone"
    ((CHECKS_FAILED++))
fi

# Check 3: Rclone remotes configured
echo -n "Checking rclone remotes... "
if command -v rclone &> /dev/null; then
    REMOTES=$(rclone listremotes 2>/dev/null)
    if [ -n "$REMOTES" ]; then
        REMOTE_COUNT=$(echo "$REMOTES" | wc -l)
        echo "✓ PASS ($REMOTE_COUNT remote(s) configured)"
        echo "  Available remotes:"
        echo "$REMOTES" | sed 's/^/    - /'
        ((CHECKS_PASSED++))
    else
        echo "✗ FAIL (no remotes configured)"
        echo "  Configure with: rclone config"
        ((CHECKS_FAILED++))
    fi
else
    echo "⊘ SKIP (rclone not available)"
fi

# Check 4: PyQt5 installation
echo -n "Checking PyQt5... "
if python3 -c "import PyQt5" 2>/dev/null; then
    echo "✓ PASS"
    ((CHECKS_PASSED++))
else
    echo "✗ FAIL (not installed)"
    echo "  Install with: pip install -r requirements.txt"
    ((CHECKS_FAILED++))
fi

# Check 5: Project files
echo -n "Checking project files... "
if [ -f "src/main.py" ] && [ -f "src/gui.py" ] && [ -f "requirements.txt" ]; then
    echo "✓ PASS"
    ((CHECKS_PASSED++))
else
    echo "✗ FAIL (missing files)"
    ((CHECKS_FAILED++))
fi

# Check 6: File permissions
echo -n "Checking file permissions... "
if [ -x "run.sh" ]; then
    echo "✓ PASS"
    ((CHECKS_PASSED++))
else
    echo "⚠ WARNING (run.sh not executable)"
    echo "  Fix with: chmod +x run.sh"
    ((CHECKS_PASSED++))
fi

echo ""
echo "======================================"
echo "Summary:"
echo "  ✓ Passed: $CHECKS_PASSED"
echo "  ✗ Failed: $CHECKS_FAILED"
echo "======================================"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo "✓ All checks passed! You're ready to run ProtonDrive Sync."
    echo ""
    echo "To start the application:"
    echo "  ./run.sh"
    echo "  OR"
    echo "  python3 -m src.main"
    exit 0
else
    echo "✗ Some checks failed. Please fix the issues above."
    echo ""
    echo "Quick fixes:"
    echo "  - Install Python 3.8+: sudo pacman -S python"
    echo "  - Install rclone: sudo pacman -S rclone"
    echo "  - Configure rclone: rclone config"
    echo "  - Install dependencies: pip install -r requirements.txt"
    exit 1
fi
