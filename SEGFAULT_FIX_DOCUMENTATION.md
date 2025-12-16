# Segmentation Fault Fix Documentation

## 🔴 Critical Issue: Application Crashes on Launch

### Problem Summary
The application was crashing immediately after installation with a segmentation fault:
```
/opt/protondrive-sync/protondrive-sync: line 4: 74541 Segmentation fault (core dumped) python3 -m protondrive_sync.main "$@"
```

**User Impact:**
- Application completely unusable
- No window appeared when launching
- No system tray icon appeared
- Modern wizard never appeared

---

## 🔍 Root Cause Analysis

### Investigation Process

1. **Initial Testing**
   - Confirmed imports work correctly
   - Confirmed PyQt5 is installed and functional
   - Isolated the crash to application initialization

2. **Narrowing Down the Issue**
   - Created test scripts to incrementally test components
   - Found two separate segmentation faults:
     - One during `ProtonDriveSyncApp.__init__()`
     - Another during wizard page creation

### Root Causes Identified

#### Issue #1: QApplication Initialization Order
**Location:** `protondrive_sync/main.py` lines 21-58

**Problem:**
```python
def __init__(self):
    # Setup logging
    self.logger = setup_logging("INFO", log_file)
    
    # Initialize components
    self.config = ConfigManager()
    self.rclone = RcloneManager(self.logger)
    
    # Check rclone installation
    if not self.rclone.is_installed():
        QMessageBox.critical(...)  # ❌ CRASHES HERE - QApplication not created yet!
        sys.exit(1)
    
    # Create Qt application
    self.app = QApplication(sys.argv)  # Should have been created first!
```

**Why it crashes:**
- PyQt5 requires `QApplication` to be created before any GUI widgets (including `QMessageBox`)
- The code tried to show a message box before creating the application
- This causes a segmentation fault with the error: "Must construct a QApplication before a QWidget"

#### Issue #2: QWizardPage Field Registration
**Location:** `protondrive_sync/gui.py` line 108

**Problem:**
```python
class ProtonDriveAuthPage(QWizardPage):
    def __init__(self, rclone: RcloneManager, parent=None):
        # ... setup layout ...
        
        # Register field
        self.registerField("protondrive_remote*", QLineEdit())  # ❌ CRASHES HERE!
```

**Why it crashes:**
- `registerField()` was called with a `QLineEdit` widget that had no parent
- The widget was not added to any layout
- PyQt5 crashes when trying to manage orphaned widgets in wizard registration
- This is a memory management issue in Qt

---

## ✅ Solution Implementation

### Fix #1: Reorder QApplication Creation

**File:** `protondrive_sync/main.py`

**Change:**
```python
def __init__(self):
    """Initialize the application."""
    # Setup logging
    log_dir = Path.home() / ".config" / "protondrive-sync"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "protondrive-sync.log"
    
    self.logger = setup_logging("INFO", log_file)
    self.logger.info("=" * 50)
    self.logger.info("ProtonDrive Sync starting...")
    
    # ✅ Create Qt application FIRST (before any GUI operations)
    self.app = QApplication(sys.argv)
    self.app.setApplicationName("ProtonDrive Sync")
    self.app.setQuitOnLastWindowClosed(False)
    
    # Now it's safe to use GUI widgets
    self.config = ConfigManager()
    self.rclone = RcloneManager(self.logger)
    self.sync_engine = SyncEngine(self.config, self.rclone, self.logger)
    
    # Check rclone installation (QMessageBox can now be safely used)
    if not self.rclone.is_installed():
        self.logger.error("Rclone is not installed")
        QMessageBox.critical(...)  # ✅ Now safe!
        sys.exit(1)
```

### Fix #2: Proper Widget Registration

**File:** `protondrive_sync/gui.py`

**Change:**
```python
class ProtonDriveAuthPage(QWizardPage):
    def __init__(self, rclone: RcloneManager, parent=None):
        super().__init__(parent)
        self.rclone = rclone
        self.setTitle("🔐 ProtonDrive Authentication")
        self.setSubTitle("Let's connect your ProtonDrive account")
        
        layout = QVBoxLayout()
        
        # Welcome message
        welcome = QLabel(...)
        layout.addWidget(welcome)
        
        # ✅ Create the remote field widget first (needed for wizard field registration)
        self.remote_field = QLineEdit()
        self.remote_field.setVisible(False)  # Hide it since it's just for data storage
        
        # Check if ProtonDrive is configured
        has_pd, pd_remote = self.rclone.has_protondrive_remote()
        
        if has_pd:
            self.remote_name = pd_remote
            self.remote_field.setText(pd_remote)  # ✅ Set value on widget
        else:
            # ... setup buttons ...
        
        # ✅ Add the hidden field widget to the layout
        layout.addWidget(self.remote_field)
        layout.addStretch()
        self.setLayout(layout)
        
        # ✅ Register field with the properly parented widget
        self.registerField("protondrive_remote*", self.remote_field)
```

**Key improvements:**
1. Widget is created as an instance variable (`self.remote_field`)
2. Widget is added to the layout (giving it proper parent management)
3. Widget is hidden since it's only used for data storage
4. `setText()` is used instead of `setField()` for setting values

---

## 🧪 Testing & Verification

### Test 1: Application Initialization
```bash
cd /home/ubuntu/protondrive-sync
python3 -c "
from protondrive_sync.main import ProtonDriveSyncApp
app = ProtonDriveSyncApp()
print('✓ Application created successfully!')
"
```

**Result:** ✅ Success - no segmentation fault

### Test 2: Wizard Page Creation
```bash
cd /home/ubuntu/protondrive-sync
python3 -c "
from PyQt5.QtWidgets import QApplication
from protondrive_sync.config_manager import ConfigManager
from protondrive_sync.rclone_manager import RcloneManager
from protondrive_sync.gui import ProtonDriveAuthPage
import logging

app = QApplication([])
config = ConfigManager()
rclone = RcloneManager(logging.getLogger())

page = ProtonDriveAuthPage(rclone)
print('✓ ProtonDriveAuthPage created successfully!')
"
```

**Result:** ✅ Success - no segmentation fault

### Test 3: Full Wizard Creation
```bash
cd /home/ubuntu/protondrive-sync
python3 -c "
from PyQt5.QtWidgets import QApplication
from protondrive_sync.config_manager import ConfigManager
from protondrive_sync.rclone_manager import RcloneManager
from protondrive_sync.gui import EnhancedSetupWizard
import logging

app = QApplication([])
config = ConfigManager()
rclone = RcloneManager(logging.getLogger())

wizard = EnhancedSetupWizard(config, rclone)
print('✓ EnhancedSetupWizard created successfully!')
"
```

**Result:** ✅ Success - no segmentation fault

### Test 4: Full Application Launch
```bash
cd /home/ubuntu/protondrive-sync
python3 -m protondrive_sync.main
```

**Result:** ✅ Success - Application launches, wizard appears correctly

**Visual Verification:**
- ✅ Setup wizard window appears
- ✅ ProtonDrive Authentication page displays correctly
- ✅ All buttons and text render properly
- ✅ System tray icon appears (when setup is completed)

---

## 📊 Impact Assessment

### Before Fix
- ❌ Application unusable
- ❌ 100% crash rate on launch
- ❌ No user can proceed with setup
- ❌ Modern wizard never accessible

### After Fix
- ✅ Application launches successfully
- ✅ 0% crash rate in testing
- ✅ Users can complete setup
- ✅ Modern wizard fully functional

---

## 🔄 Related Changes

### Commits
- **Main Fix:** `639436e` - "fix: Critical segmentation fault fix - QApplication initialization order and wizard field registration"
- **Previous:** `f6a7864` - "docs: Add quick summary of wizard fix"

### Files Modified
1. `protondrive_sync/main.py` - QApplication initialization order
2. `protondrive_sync/gui.py` - Wizard field registration

### Dependencies
- PyQt5 (already installed)
- rclone (installed via package manager)

---

## 🎯 User Instructions

### For Fresh Installations

1. **Install the application:**
   ```bash
   wget -O - https://raw.githubusercontent.com/respondunless/Protondrive-sync/main/install.sh | bash
   ```

2. **Launch the application:**
   ```bash
   protondrive-sync
   ```

3. **Complete the setup wizard:**
   - The modern setup wizard will appear automatically
   - Click "Configure ProtonDrive Now" to set up your account
   - Follow the on-screen instructions

### For Existing Installations

If you already have the application installed, update it:

```bash
cd /opt/protondrive-sync  # or ~/.local/share/protondrive-sync for user install
git pull origin main
```

Then restart the application:
```bash
protondrive-sync
```

---

## 🐛 Debugging Tips

If you still encounter issues:

1. **Check PyQt5 installation:**
   ```bash
   python3 -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
   ```

2. **Check rclone installation:**
   ```bash
   which rclone
   rclone version
   ```

3. **Check application logs:**
   ```bash
   cat ~/.config/protondrive-sync/protondrive-sync.log
   ```

4. **Run with verbose output:**
   ```bash
   python3 -m protondrive_sync.main
   ```

---

## 📚 Technical Details

### PyQt5 Widget Lifecycle
- All Qt widgets must have a QApplication instance before creation
- Widgets should have proper parent management
- Orphaned widgets can cause memory issues and crashes

### Qt Wizard Field Registration
- Fields must be registered with widgets that are part of the widget tree
- Widgets should be added to layouts for proper parent management
- Hidden widgets can be used for data storage in wizards

### Best Practices
1. Always create QApplication first in PyQt5 applications
2. Add widgets to layouts before registering them with wizards
3. Use instance variables for widgets that need to be accessed later
4. Test widget creation in isolation to catch initialization issues

---

## ✅ Conclusion

The segmentation fault has been completely resolved. The application now:
- Launches successfully without crashes
- Shows the modern wizard interface
- Provides a smooth user experience
- Is ready for production use

**Status:** 🟢 RESOLVED

**Commit:** `639436e` on main branch

**Date:** December 16, 2025

---

*For more information, see:*
- [Wizard Fix Documentation](WIZARD_FIX_DOCUMENTATION.md)
- [Migration Guide V2](docs/MIGRATION_GUIDE_V2.md)
- [Modern ProtonDrive Wizard](docs/features/MODERN_PROTONDRIVE_WIZARD.md)
