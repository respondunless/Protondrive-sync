# ProtonDrive Sync - Quick Start Guide

Get up and running with ProtonDrive Sync in just a few minutes!

## Prerequisites Check

### 1. Check Python Installation

```bash
python --version
# Should show Python 3.8 or higher
```

If not installed:
```bash
# Arch/CachyOS
sudo pacman -S python
```

### 2. Install Rclone

```bash
# Arch/CachyOS
sudo pacman -S rclone

# Verify installation
rclone version
```

### 3. Configure ProtonDrive with Rclone

```bash
rclone config
```

Follow these steps:
1. Press `n` for "New remote"
2. Name it (e.g., "protondrive")
3. Choose ProtonDrive option (search for "protondrive")
4. Follow the authentication prompts
5. Test with: `rclone lsd protondrive:`

## Installation

### Option 1: Quick Run (No Installation)

```bash
# Navigate to the project directory
cd /path/to/protondrive-sync

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.main
```

### Option 2: Install as Package

```bash
# Navigate to the project directory
cd /path/to/protondrive-sync

# Install the package
pip install -e .

# Run from anywhere
protondrive-sync
```

### Option 3: Virtual Environment (Recommended)

```bash
# Create virtual environment
cd /path/to/protondrive-sync
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.main
```

## First Run Setup

1. **Launch the Application**
   - The setup wizard will appear automatically

2. **Configure Your Remote**
   - Select your ProtonDrive remote from the dropdown
   - Click "Test Remote" to verify it works
   - You should see a green checkmark

3. **Choose Local Folder**
   - Click "Browse" and select where you want files synced
   - Example: `/home/yourusername/ProtonDrive`
   - Make sure you have write permissions

4. **Set Auto-Sync (Optional)**
   - Check "Enable automatic sync" if desired
   - Set sync interval (default: 30 minutes)

5. **Save Configuration**
   - Click "OK" to save and close the wizard

## Basic Usage

### Manual Sync

1. Open the application window
2. Click the "▶️ Sync Now" button
3. Watch the activity log for progress

### Auto-Sync

1. Open Settings (⚙️ button)
2. Enable "Enable automatic sync"
3. Set desired interval
4. Click OK

### System Tray

- **Double-click icon** - Open main window
- **Right-click icon** - Quick menu
  - Start/Stop Auto-Sync
  - Sync Now
  - Quit

## Troubleshooting

### Application Won't Start

```bash
# Run with error output
python -m src.main

# Check logs
cat ~/.config/protondrive-sync/protondrive-sync.log
```

### Rclone Not Found

```bash
# Install rclone
sudo pacman -S rclone

# Verify it's in PATH
which rclone
```

### Remote Not Accessible

```bash
# Test rclone configuration
rclone lsd your-remote-name:

# If it fails, reconfigure
rclone config
```

### Permission Denied on Local Folder

```bash
# Check folder permissions
ls -la /path/to/sync/folder

# Create folder with correct permissions
mkdir -p ~/ProtonDrive
chmod 755 ~/ProtonDrive
```

## Daily Workflow

### Morning Routine

1. Application should already be running in system tray
2. Check for sync status (right-click tray icon)
3. Manual sync if needed

### Working with Files

1. Files sync from ProtonDrive → Local folder
2. Work on files locally
3. Changes will be synced on next sync cycle
4. **Note:** This is a one-way sync (ProtonDrive → Local)

### Evening Routine

1. Check activity log for any sync errors
2. Leave application running for auto-sync
3. Or quit from tray menu if desired

## Advanced Configuration

### Config File Location

```
~/.config/protondrive-sync/config.json
```

### Manual Config Edit

```bash
# Edit configuration
nano ~/.config/protondrive-sync/config.json

# Restart application after editing
```

### View Logs

```bash
# Real-time log viewing
tail -f ~/.config/protondrive-sync/protondrive-sync.log

# View recent logs
tail -50 ~/.config/protondrive-sync/protondrive-sync.log
```

## Tips & Best Practices

1. **Start Small**
   - Test with a small subset of files first
   - Verify sync works correctly before syncing everything

2. **Regular Syncs**
   - Enable auto-sync for consistent file updates
   - Set interval based on your needs (15-60 minutes)

3. **Monitor Logs**
   - Check activity log occasionally
   - Look for sync errors or warnings

4. **Backup**
   - Local folder is synced from ProtonDrive
   - Keep important files backed up on ProtonDrive

5. **System Resources**
   - Application uses minimal resources when idle
   - Syncing large files may use more bandwidth

## Uninstallation

```bash
# If installed with pip
pip uninstall protondrive-sync

# Remove configuration
rm -rf ~/.config/protondrive-sync

# Remove virtual environment (if used)
rm -rf /path/to/protondrive-sync/venv
```

## Getting Help

- **Check README.md** - Comprehensive documentation
- **View Logs** - `~/.config/protondrive-sync/protondrive-sync.log`
- **Rclone Docs** - https://rclone.org/protondrive/
- **GitHub Issues** - Report bugs or request features

## Next Steps

- ✅ Application is running
- ✅ First sync completed
- 📖 Read the full README.md for advanced features
- ⚙️ Customize settings to your preferences
- 🚀 Enjoy automatic ProtonDrive syncing!

---

**Happy Syncing! 🚀**
