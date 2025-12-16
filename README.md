# ProtonDrive Sync

A Python-based desktop application for syncing ProtonDrive files to your local system using rclone. Features a clean GUI, system tray integration, and automatic sync capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

---

## 🎉 **SUPER EASY INSTALLATION** - For New Linux Users!

> **New to Linux?** No problem! We've made installation incredibly simple. Just run one command and you're done! 🚀

### One-Command Install (Recommended)

Choose any of these options:

**Option 1:** Using curl
```bash
curl -sSL https://raw.githubusercontent.com/respondunless/Protondrive-sync/main/install.sh | bash
```

**Option 2:** Using wget
```bash
wget -qO- https://raw.githubusercontent.com/respondunless/Protondrive-sync/main/install.sh | bash
```

**Option 3:** Clone and install
```bash
git clone https://github.com/respondunless/Protondrive-sync.git
cd Protondrive-sync
./install.sh
```

### What the Installer Does

The installer is **super friendly** and will:

✅ Detect your Linux distribution automatically  
✅ Install ALL dependencies (Python, PyQt5, rclone, etc.)  
✅ Set up the application properly  
✅ Add ProtonDrive Sync to your application menu  
✅ Optionally set up autostart on login  
✅ Guide you through rclone configuration  
✅ Launch the app for you!

### What to Expect

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           ProtonDrive Sync - Easy Installer 🚀            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

Welcome to the ProtonDrive Sync installer!
This script will guide you through a super easy installation.

→ Detecting your Linux distribution...
✓ Detected: Your Linux Distro

→ Installing dependencies 📦
✓ System dependencies installed
✓ Python packages ready

→ Installing application files...
✓ Application files installed

→ Creating desktop integration...
✓ Desktop entry created - app will appear in your application menu!

╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              Installation Complete! ★★★                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

### After Installation

1. **Find the app** in your application menu (search for "ProtonDrive Sync")
2. **Or run from terminal:** `protondrive-sync`
3. **Follow the setup wizard** to configure your ProtonDrive connection
4. **Start syncing!** It's that easy! 🎊

### First-Time rclone Setup

If you haven't configured rclone yet, the app will guide you! Just:

1. Click **"Configure rclone"** button in the setup wizard
2. Choose **'n'** for new remote
3. Name it **'protondrive'**
4. Select **'Proton Drive'** from the list
5. Follow the authentication steps
6. Done! 🎉

### Uninstalling

If you ever want to remove ProtonDrive Sync:

```bash
protondrive-sync-uninstall
```

Or navigate to the installation directory and run:
```bash
./uninstall.sh
```

The uninstaller will ask if you want to keep your configuration and data.

### Troubleshooting Installation

<details>
<summary><b>Click here if you encounter installation issues</b></summary>

#### "Permission denied" error

Run the installer with proper permissions:
```bash
chmod +x install.sh
./install.sh
```

#### "Command not found: curl" or "wget"

Install curl or wget first:
```bash
# For Arch-based systems
sudo pacman -S curl

# For Debian/Ubuntu
sudo apt-get install curl

# For Fedora
sudo dnf install curl
```

#### PyQt5 installation fails

The installer will try to install PyQt5 via your system package manager automatically. If it still fails:

```bash
# For Arch-based systems
sudo pacman -S python-pyqt5

# For Debian/Ubuntu
sudo apt-get install python3-pyqt5

# For Fedora
sudo dnf install python3-qt5
```

#### App doesn't appear in application menu

Try updating your desktop database:
```bash
update-desktop-database ~/.local/share/applications/
```

Or logout and login again.

#### "~/.local/bin not in PATH" warning

Add this line to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc
```

</details>

---

## ✨ Features

- 🖥️ **System Tray Integration** - Runs quietly in the background with easy access from system tray
- 🎨 **Clean PyQt5 GUI** - User-friendly interface for managing sync operations
- 🔄 **Automatic Sync** - Configure interval-based automatic syncing
- 📝 **Manual Sync** - Trigger sync operations on-demand
- ⚙️ **Configuration Management** - Easy setup wizard for first-time configuration
- 📊 **Activity Log** - Real-time sync progress and activity monitoring
- 🔔 **Desktop Notifications** - Get notified about sync status and completion
- 🛡️ **Error Handling** - Graceful error handling with detailed logging
- 🧵 **Background Processing** - Non-blocking sync operations using threading

## 📋 Prerequisites

Before installing ProtonDrive Sync, ensure you have:

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **Rclone** - Required for syncing with ProtonDrive
   ```bash
   # On Arch Linux / CachyOS
   sudo pacman -S rclone
   
   # On other distributions
   # See https://rclone.org/install/
   ```

3. **ProtonDrive Account** - With rclone configured
   ```bash
   rclone config
   ```
   Follow the prompts to set up your ProtonDrive remote. See [Rclone ProtonDrive documentation](https://rclone.org/protondrive/) for details.

## 🚀 Manual Installation (Advanced Users)

> **Note:** Most users should use the [Super Easy Installation](#-super-easy-installation---for-new-linux-users) method above! This section is for advanced users who want more control.

### Prerequisites

Ensure you have:
- Python 3.8+
- pip
- rclone

### Method 1: Install from source

1. **Clone the repository**
   ```bash
   git clone https://github.com/respondunless/Protondrive-sync.git
   cd Protondrive-sync
   ```

2. **Install dependencies**
   ```bash
   pip install PyQt5
   ```

3. **Run directly**
   ```bash
   python -m src.main
   ```

### Method 2: Using the automated installer

```bash
./install.sh
```

This gives you more control over the installation process.

## 🔧 First-Time Setup

1. **Launch the application**
   ```bash
   protondrive-sync
   ```
   Or if installed locally:
   ```bash
   python -m src.main
   ```

2. **Setup Wizard**
   - On first run, you'll see a setup wizard
   - Select your ProtonDrive rclone remote from the dropdown
   - Click "Test Remote" to verify connectivity
   - Choose a local folder for syncing your files
   - Configure auto-sync settings (optional)
   - Click OK to save configuration

3. **Start Syncing**
   - Click "Sync Now" for an immediate sync
   - Or enable auto-sync from the settings

## 📖 Usage

### Main Window

The main window provides:
- **Sync Status** - Current sync state and last sync time
- **Configuration** - View and edit your sync settings
- **Sync Controls** - Manual sync and cancel buttons
- **Activity Log** - Real-time sync progress and logs

### System Tray

Right-click the system tray icon for quick actions:
- **Open ProtonDrive Sync** - Show the main window
- **Start/Stop Auto-Sync** - Toggle automatic syncing
- **Sync Now** - Trigger immediate sync
- **Quit** - Exit the application

Double-click the tray icon to open the main window.

### Settings

Click the "⚙️ Settings" button to:
- Change ProtonDrive remote
- Update local sync folder
- Enable/disable auto-sync
- Adjust sync interval

## 🗂️ Project Structure

```
protondrive-sync/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Application entry point
│   ├── config_manager.py     # Configuration handling
│   ├── rclone_manager.py     # Rclone integration
│   ├── sync_engine.py        # Sync logic and threading
│   ├── gui.py                # Main window and setup wizard
│   ├── tray.py               # System tray implementation
│   └── utils.py              # Helper functions
├── requirements.txt          # Python dependencies
├── setup.py                  # Installation script
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔍 Configuration

Configuration is stored in `~/.config/protondrive-sync/config.json`:

```json
{
    "rclone_remote": "protondrive",
    "local_folder": "/home/user/ProtonDrive",
    "auto_sync_enabled": true,
    "sync_interval_minutes": 30,
    "notifications_enabled": true,
    "log_level": "INFO"
}
```

You can manually edit this file or use the settings dialog in the application.

## 📝 Logs

Application logs are stored in:
```
~/.config/protondrive-sync/protondrive-sync.log
```

View logs for troubleshooting:
```bash
tail -f ~/.config/protondrive-sync/protondrive-sync.log
```

## 🛠️ Troubleshooting

### Rclone not found

**Problem:** Application shows "Rclone not found" error.

**Solution:**
```bash
# Install rclone
sudo pacman -S rclone  # Arch/CachyOS
# or follow https://rclone.org/install/

# Verify installation
rclone version
```

### Remote not accessible

**Problem:** Setup wizard shows "Remote not accessible" error.

**Solution:**
1. Verify rclone configuration:
   ```bash
   rclone listremotes
   rclone lsd your-remote-name:
   ```
2. Reconfigure if needed:
   ```bash
   rclone config
   ```

### Sync fails with permission errors

**Problem:** Sync fails due to permission denied errors.

**Solution:**
- Ensure the local sync folder has write permissions
- Check that you're not syncing to a system directory
- Try syncing to a folder in your home directory

### Application doesn't start

**Problem:** Application window doesn't appear.

**Solution:**
1. Check if it's running in the system tray (look for the icon)
2. Run from terminal to see error messages:
   ```bash
   python -m src.main
   ```
3. Check logs:
   ```bash
   cat ~/.config/protondrive-sync/protondrive-sync.log
   ```

### Auto-sync not working

**Problem:** Auto-sync doesn't trigger.

**Solution:**
1. Verify auto-sync is enabled in settings
2. Check the sync interval setting
3. Look for errors in the activity log
4. Restart the application

## 🔐 Security Considerations

- **Credentials:** This application uses rclone's secure credential storage
- **Local Storage:** Synced files are stored locally without additional encryption
- **Network:** All connections to ProtonDrive use rclone's secure protocols
- **Permissions:** The application only accesses the configured sync folder

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Rclone** - For providing the excellent sync backend
- **ProtonDrive** - For secure cloud storage
- **PyQt5** - For the GUI framework

## 📞 Support

If you encounter issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review application logs
3. Open an issue on GitHub
4. Check [Rclone documentation](https://rclone.org/protondrive/)

## 🗺️ Roadmap

Future enhancements planned:

- [ ] Bidirectional sync support
- [ ] Selective folder sync
- [ ] Conflict resolution UI
- [ ] Custom sync filters
- [ ] Multiple remote support
- [ ] Bandwidth limiting
- [ ] Dark mode theme
- [ ] Windows and macOS support

## ℹ️ Technical Details

### Dependencies

- **PyQt5** (>=5.15.0) - GUI framework
- **Python Standard Library:**
  - `subprocess` - Rclone execution
  - `threading` - Background sync
  - `json` - Configuration management
  - `logging` - Activity logging
  - `pathlib` - Path operations

### System Requirements

- **OS:** Linux (Arch-based distributions tested, others should work)
- **Python:** 3.8 or higher
- **RAM:** 100MB+ (depends on sync size)
- **Disk:** Varies based on ProtonDrive content size

### Architecture

The application follows a modular architecture:
- **Config Layer:** Manages application configuration
- **Rclone Layer:** Interfaces with rclone CLI
- **Sync Layer:** Handles sync logic and threading
- **UI Layer:** PyQt5 GUI and system tray
- **Utility Layer:** Common helper functions

---

**Made with ❤️ for the ProtonDrive and Linux community**
