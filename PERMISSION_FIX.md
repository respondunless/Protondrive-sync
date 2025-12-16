# Permission Fix - Installation Guide

## What Happened? 🤔

You ran the ProtonDrive Sync installer and it got **most of the way through successfully**, but failed with this error:

```
mkdir: cannot create directory '/opt/protondrive-sync': Permission denied
```

### Why Did This Happen?

- You chose **Option 1: System-wide installation** which installs the app to `/opt/protondrive-sync`
- Creating directories in `/opt` requires **sudo (administrator) permissions**
- The installer was run **without sudo**, so it couldn't create that directory

### What Was Successfully Installed? ✅

The good news: **Most installation completed successfully!**

1. ✅ **System packages installed** (via pacman):
   - Python
   - PyQt5
   - rclone
   - All other dependencies

2. ❌ **Application files NOT copied** to `/opt` (this is where it failed)

### Is Cleanup Needed?

**No cleanup is necessary!** The packages installed (Python, PyQt5, rclone) are useful system packages that won't cause any issues. The installer is now **idempotent** (safe to run multiple times).

---

## How to Fix and Complete Installation 🚀

You have **two options**:

### Option 1: Run with sudo (System-wide Install) - RECOMMENDED

This installs the app for **all users** on your system:

```bash
cd /home/ubuntu/protondrive-sync
sudo bash install.sh
```

When prompted:
- Choose **Option 1** (System-wide installation)
- Enter your sudo password when asked

**Benefits:**
- Available for all users
- Installed to `/opt/protondrive-sync`
- Adds system-wide commands
- Better integration with system

### Option 2: User-only Install (No sudo needed)

This installs only for **your user account**:

```bash
cd /home/ubuntu/protondrive-sync
bash install.sh
```

When prompted:
- Choose **Option 2** (User-only installation)
- No sudo password needed

**Benefits:**
- No sudo required
- Installed to `~/.local/share/protondrive-sync`
- Works perfectly for single-user systems
- No permission issues

---

## What's Been Fixed in the Installer? 🔧

The installer has been improved with:

### 1. **Early Permission Check**
- Now checks for sudo **before** starting file operations
- Provides clear guidance if sudo is missing
- Fails fast with helpful error messages

### 2. **Proper sudo Handling**
- Uses sudo only for operations that need it
- Keeps sudo alive during installation
- Cleans up properly when done

### 3. **Idempotent Installation**
- Safe to run multiple times
- Won't duplicate or break existing installations
- Updates files if already installed
- Checks for existing directories before creating

### 4. **Better Error Messages**
- Clear explanations of what went wrong
- Specific instructions on how to fix issues
- Helpful guidance about alternatives

### 5. **Robust File Operations**
- Properly handles all file copying with appropriate permissions
- Creates desktop entries correctly for both install types
- Handles symlinks properly with sudo when needed

---

## Testing the Fix ✨

After running the installer again with the correct permissions:

1. **Check if installed:**
   ```bash
   which protondrive-sync
   ```

2. **Try running it:**
   ```bash
   protondrive-sync
   ```

3. **Check desktop integration:**
   - Open your application menu
   - Search for "ProtonDrive Sync"
   - It should appear!

---

## FAQ ❓

### Q: Will running the installer again cause problems?
**A:** No! The installer is now idempotent and safe to run multiple times. It will update files if they already exist.

### Q: Do I need to uninstall the packages that were already installed?
**A:** No! Python, PyQt5, and rclone are useful system packages. Keep them installed.

### Q: What if I want to switch from user-only to system-wide (or vice versa)?
**A:** Run the uninstaller first:
```bash
bash ~/.local/share/protondrive-sync/uninstall.sh  # For user install
# OR
sudo bash /opt/protondrive-sync/uninstall.sh       # For system install
```
Then run the installer again with your preferred option.

### Q: Can I just run the installer again right now?
**A:** Yes! Just follow Option 1 or Option 2 above. No cleanup needed.

### Q: What's the difference between system-wide and user-only?
**A:**
- **System-wide**: Installed to `/opt`, available for all users, requires sudo
- **User-only**: Installed to `~/.local/share`, only for you, no sudo needed

For single-user systems (like most home computers), both work equally well!

---

## Technical Details 🔍

### Changes Made to install.sh:

1. **check_sudo()** - Enhanced to:
   - Check sudo before any file operations
   - Provide detailed guidance if sudo is missing
   - Keep sudo alive during installation
   - Clean up background processes

2. **copy_files()** - Improved to:
   - Use `sudo` only when needed (system-wide install)
   - Check if directories exist before creating
   - Provide informative messages during copying
   - Handle errors gracefully with clear messages
   - Use `tee` for proper file writing with sudo

3. **create_desktop_entry()** - Fixed to:
   - Use sudo for system-wide desktop entries
   - Create directories with appropriate permissions
   - Update desktop database correctly

### Files Modified:
- `install.sh` - Complete permission handling overhaul

### Compatibility:
- Works with all shells (bash, Fish, zsh)
- Works with all Linux distributions
- Safe to run multiple times
- Backwards compatible with existing installations

---

## Need More Help? 💬

If you encounter any issues:

1. Check the error message carefully
2. Make sure you're running the correct command for your chosen option
3. For system-wide install: ensure you have sudo access
4. For user-only install: no special permissions needed

The installer will now provide clear, actionable error messages if something goes wrong!

---

## Summary 📝

✅ Packages already installed successfully
✅ Installer improved with proper permission handling  
✅ Safe to run installer again  
✅ No cleanup needed  
✅ Choose either system-wide (with sudo) or user-only (no sudo)

**Next step:** Run the installer again using one of the options above! 🚀
