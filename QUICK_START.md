# 🚀 Quick Start Guide - ProtonDrive Sync

Welcome! This guide will get you up and running in minutes.

## Step 1: Install (One Command!)

Open a terminal and run **any** of these commands:

### Option A: Using curl
```bash
curl -sSL https://raw.githubusercontent.com/respondunless/Protondrive-sync/main/install.sh | bash
```

### Option B: Using wget
```bash
wget -qO- https://raw.githubusercontent.com/respondunless/Protondrive-sync/main/install.sh | bash
```

### Option C: Clone and install
```bash
git clone https://github.com/respondunless/Protondrive-sync.git
cd Protondrive-sync
./install.sh
```

## Step 2: Configure rclone (First Time Only)

If you haven't set up rclone with ProtonDrive yet:

1. The installer will ask if you want to configure it
2. Choose **'n'** for new remote
3. Name it **'protondrive'** (or anything you like)
4. Select **'Proton Drive'** from the list
5. Follow the authentication steps
6. Done!

Or configure it manually later:
```bash
rclone config
```

## Step 3: Launch the App

### From Application Menu
1. Press your Super/Windows key
2. Type **"ProtonDrive Sync"**
3. Click to launch

### From Terminal
```bash
protondrive-sync
```

## Step 4: Set Up Sync

The setup wizard will guide you:

1. **Select your ProtonDrive remote** from the dropdown
2. **Click "Test Remote"** to verify connection
3. **Choose local folder** (default: ~/ProtonDrive)
4. **Enable auto-sync** (recommended)
5. **Click OK** to finish

That's it! 🎉

## Using the App

### Main Features

- **Sync Now** - Manually trigger a sync
- **Auto-sync** - Automatically sync at regular intervals
- **Activity Log** - See what's happening in real-time
- **System Tray** - App runs in background, accessible from tray

### System Tray Menu

Right-click the tray icon for:
- Open window
- Sync now
- Start/Stop auto-sync
- Quit

## Need Help?

### App won't start?

Check the logs:
```bash
cat ~/.config/protondrive-sync/protondrive-sync.log
```

### rclone not configured?

Run this and follow the prompts:
```bash
rclone config
```

### Can't find the app in menu?

Try:
```bash
update-desktop-database ~/.local/share/applications/
```

Or just run from terminal:
```bash
protondrive-sync
```

## Uninstall

If you ever want to remove the app:

```bash
protondrive-sync-uninstall
```

The uninstaller will ask if you want to keep your configuration.

## Tips & Tricks

### Autostart on Login

The installer can set this up automatically, or you can enable it later in your system's "Startup Applications" settings.

### Change Sync Location

Click **Settings** (⚙️) in the app to change where files are synced.

### Multiple Remotes

You can set up multiple rclone remotes and switch between them in Settings.

### Sync Interval

Default is 30 minutes. Adjust in Settings based on your needs:
- **5 minutes** - For frequent changes
- **30 minutes** - Balanced (recommended)
- **60+ minutes** - For large files or slow connections

## Common Issues

| Problem | Solution |
|---------|----------|
| "Permission denied" | Make sure install script is executable: `chmod +x install.sh` |
| PyQt5 won't install | Use system package manager (installer does this automatically) |
| App in tray but can't see icon | Check your system tray settings, may need to whitelist |
| Sync is slow | Increase sync interval or check rclone bandwidth settings |

## Getting More Help

- 📖 [Full README](README.md)
- 🐛 [Report Issues](https://github.com/respondunless/Protondrive-sync/issues)
- 📚 [rclone Documentation](https://rclone.org/protondrive/)

---

**Happy syncing! 🎊**

Made with ❤️ for Linux users
