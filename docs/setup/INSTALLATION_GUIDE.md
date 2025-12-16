# 📦 Complete Installation Guide - ProtonDrive Sync

This guide covers everything you need to know about installing ProtonDrive Sync, from the easiest automated method to manual installation.

---

## 🌟 Method 1: One-Command Installation (Recommended for Everyone!)

This is the **easiest** way to install ProtonDrive Sync. Perfect for beginners!

### Step 1: Open a Terminal

- **GNOME/Ubuntu:** Press `Ctrl + Alt + T`
- **KDE:** Press `Ctrl + Alt + T` or search for "Konsole"
- **Any Desktop:** Search for "Terminal" in your application menu

### Step 2: Run the Installation Command

Copy and paste **one** of these commands into your terminal:

#### Using curl:
```bash
curl -sSL https://raw.githubusercontent.com/respondunless/Protondrive-sync/main/install.sh | bash
```

#### Using wget:
```bash
wget -qO- https://raw.githubusercontent.com/respondunless/Protondrive-sync/main/install.sh | bash
```

#### Or download first, then install:
```bash
git clone https://github.com/respondunless/Protondrive-sync.git
cd Protondrive-sync
./install.sh
```

### Step 3: Follow the Prompts

The installer will ask you a few simple questions:

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           ProtonDrive Sync - Easy Installer 🚀            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

Welcome to the ProtonDrive Sync installer!
This script will guide you through a super easy installation.

→ Detecting your Linux distribution...
✓ Detected: Ubuntu 22.04.3 LTS

Where would you like to install the application?
  1) System-wide (requires sudo, available for all users)
  2) User-only (no sudo required, only for you)

Choose [1-2]:
```

**What to choose:**
- Choose **1** if you want the app available for all users on your system (requires admin password)
- Choose **2** if you want it just for yourself (no admin password needed)

```
Would you like the app to start automatically when you log in? [y/N]:
```

**Recommendation:** Type `n` (no) for now. You can enable this later if you want.

### Step 4: Wait for Installation

The installer will now:
- ✓ Install Python, PyQt5, rclone, and other dependencies
- ✓ Set up the application files
- ✓ Create desktop menu entry
- ✓ Set up commands

This takes 30 seconds to 2 minutes depending on your system.

### Step 5: Configure rclone (If Needed)

If you haven't configured rclone yet, the installer will ask:

```
⚠ rclone doesn't seem to be configured yet
Would you like to configure rclone now? [Y/n]:
```

Type `y` and press Enter. Then follow these steps in the rclone configuration:

```
→ Starting rclone configuration...

When prompted:
  1. Choose 'n' for new remote
  2. Name it 'protondrive'
  3. Select 'Proton Drive' from the list
  4. Follow the authentication steps

Press Enter to continue...
```

**In the rclone config menu:**

1. Type `n` and press Enter (new remote)
2. Name: Type `protondrive` and press Enter
3. Storage: Type the number for "Proton Drive" and press Enter
4. Username: Enter your Proton email
5. Password: Enter your Proton password (or app password)
6. 2FA: Enter your 2FA code if enabled
7. Type `q` to quit when done

### Step 6: Launch the App

```
Would you like to launch ProtonDrive Sync now? [Y/n]:
```

Type `y` and the app will open!

---

## 📱 Method 2: Manual Installation (Advanced Users)

For users who want more control or prefer manual installation.

### Prerequisites

Install these first:

```bash
# On Arch/Manjaro/CachyOS
sudo pacman -S python python-pip python-pyqt5 rclone git

# On Ubuntu/Debian/Mint
sudo apt-get update
sudo apt-get install python3 python3-pip python3-pyqt5 rclone git

# On Fedora
sudo dnf install python3 python3-pip python3-qt5 rclone git

# On openSUSE
sudo zypper install python3 python3-pip python3-qt5 rclone git
```

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/respondunless/Protondrive-sync.git
   cd Protondrive-sync
   ```

2. **Install Python dependencies:**
   ```bash
   pip install --user PyQt5
   ```

3. **Make scripts executable:**
   ```bash
   chmod +x install.sh
   ```

4. **Run the installer:**
   ```bash
   ./install.sh
   ```

   Or run directly without installation:
   ```bash
   python3 -m src.main
   ```

---

## 🔧 First-Time Setup

After installation, launch ProtonDrive Sync and you'll see the **Setup Wizard**.

### Setup Wizard Walkthrough

```
╔══════════════════════════════════════════════════════╗
║  🚀 Welcome to ProtonDrive Sync!                    ║
║                                                      ║
║  Let's get you set up in just a few steps.          ║
║  This will only take a minute!                      ║
║                                                      ║
║  Don't worry - we'll guide you through everything.  ║
╚══════════════════════════════════════════════════════╝
```

**Step 1: Select Your ProtonDrive Remote**

- If you see your remote in the dropdown: Select it
- If you see "No remotes found": Click **"Configure rclone"** button

**Step 2: Test Remote Connection**

- Click **"Test Remote"** button
- You should see: ✅ "Remote is accessible"
- If not, check your rclone configuration

**Step 3: Choose Local Sync Folder**

- Default: `~/ProtonDrive` (recommended)
- Or click **"Browse"** to choose a different location
- Make sure you have enough disk space!

**Step 4: Configure Auto Sync**

- ✅ Enable automatic sync (recommended)
- Set interval: 30 minutes (default, adjust as needed)

**Step 5: Confirm and Start**

- Click **OK**
- Confirm your settings
- Done! Your files will start syncing

---

## 🎯 Post-Installation

### Finding the App

**Method 1: Application Menu**
1. Press Super/Windows key
2. Type "ProtonDrive Sync"
3. Click the icon

**Method 2: Terminal**
```bash
protondrive-sync
```

**Method 3: System Tray**
- Look for the ProtonDrive Sync icon in your system tray
- Right-click for quick actions

### Verifying Installation

Check if everything is working:

```bash
# Check if command is available
which protondrive-sync

# Check rclone configuration
rclone listremotes

# Check configuration directory
ls ~/.config/protondrive-sync/
```

---

## 🐛 Troubleshooting

### Installation Issues

#### "Permission denied" Error

**Problem:** Can't run install script

**Solution:**
```bash
chmod +x install.sh
./install.sh
```

#### "curl not found" or "wget not found"

**Problem:** Command not available

**Solution:** Install curl or wget first:
```bash
# Arch/Manjaro
sudo pacman -S curl

# Ubuntu/Debian
sudo apt-get install curl

# Fedora
sudo dnf install curl
```

#### PyQt5 Installation Fails

**Problem:** pip can't install PyQt5

**Solution:** Use system package manager:
```bash
# Arch/Manjaro
sudo pacman -S python-pyqt5

# Ubuntu/Debian
sudo apt-get install python3-pyqt5

# Fedora
sudo dnf install python3-qt5
```

#### "No remotes found" in Setup Wizard

**Problem:** rclone not configured

**Solution:**
1. Click **"Configure rclone"** in setup wizard
2. Or run manually: `rclone config`
3. Set up ProtonDrive remote
4. Click **"Refresh List"** in setup wizard

### Runtime Issues

#### App Won't Start

**Check 1: Is it already running?**
```bash
pgrep -f protondrive-sync
```

**Check 2: Check logs**
```bash
cat ~/.config/protondrive-sync/protondrive-sync.log
```

**Check 3: Run from terminal to see errors**
```bash
python3 -m src.main
```

#### App Not in Application Menu

**Solution 1: Update desktop database**
```bash
update-desktop-database ~/.local/share/applications/
```

**Solution 2: Logout and login again**

**Solution 3: Run from terminal**
```bash
protondrive-sync
```

#### Sync Not Working

**Check 1: Test remote connection**
```bash
rclone lsd protondrive:
```

**Check 2: Check permissions on sync folder**
```bash
ls -la ~/ProtonDrive
```

**Check 3: Check logs**
```bash
tail -f ~/.config/protondrive-sync/protondrive-sync.log
```

---

## 🗑️ Uninstallation

### Easy Uninstall

Run the uninstaller:

```bash
protondrive-sync-uninstall
```

Or:

```bash
# For system installation
/opt/protondrive-sync/uninstall.sh

# For user installation
~/.local/share/protondrive-sync/uninstall.sh
```

### What Gets Removed

The uninstaller will remove:
- ✓ Application files
- ✓ Desktop entries
- ✓ Command symlinks
- ✓ Autostart entries

It will **ask** before removing:
- Configuration files (~/.config/protondrive-sync/)
- Your synced files (your choice)

### Clean Uninstall

For a complete clean removal:

```bash
# Run uninstaller
protondrive-sync-uninstall

# Manually remove config if you kept it
rm -rf ~/.config/protondrive-sync/

# Optionally remove rclone config
# (Only if you don't use rclone for anything else!)
# rm -rf ~/.config/rclone/
```

---

## 💡 Tips & Best Practices

### 1. Choose the Right Sync Interval

- **5-15 minutes:** For frequently changing files
- **30 minutes:** Balanced (recommended for most users)
- **1-2 hours:** For large files or slow connections
- **Manual only:** For complete control

### 2. Folder Organization

Recommended folder structure:
```
~/ProtonDrive/
├── Documents/
├── Photos/
├── Projects/
└── Backups/
```

### 3. Disk Space Management

Check available space before syncing:
```bash
df -h ~
```

### 4. Network Considerations

- Use wired connection for initial large sync
- Avoid syncing over mobile hotspot (large data usage)
- Check bandwidth settings in rclone if needed

### 5. Security

- Use strong Proton password
- Enable 2FA on Proton account
- Keep rclone config file secure (~/.config/rclone/)
- Don't share your config files

---

## 📞 Getting Help

### Documentation

- 📖 [README.md](README.md) - Full documentation
- 🚀 [QUICK_START.md](QUICK_START.md) - Quick reference
- 📦 This guide - Detailed installation help

### Community Support

- 🐛 [GitHub Issues](https://github.com/respondunless/Protondrive-sync/issues) - Report bugs
- 💬 [Discussions](https://github.com/respondunless/Protondrive-sync/discussions) - Ask questions
- 📚 [rclone Docs](https://rclone.org/protondrive/) - rclone help

### Logs and Debugging

Application log location:
```
~/.config/protondrive-sync/protondrive-sync.log
```

View live logs:
```bash
tail -f ~/.config/protondrive-sync/protondrive-sync.log
```

---

## ✅ Installation Checklist

Use this checklist to verify your installation:

- [ ] Terminal opened successfully
- [ ] Installation command executed
- [ ] Dependencies installed (Python, PyQt5, rclone)
- [ ] Application files installed
- [ ] Desktop entry created
- [ ] Command `protondrive-sync` works
- [ ] rclone configured with ProtonDrive
- [ ] Setup wizard completed
- [ ] Remote connection tested successfully
- [ ] Local sync folder created
- [ ] First sync completed
- [ ] App appears in application menu
- [ ] System tray icon visible

If all items are checked ✅ - Congratulations! You're all set! 🎉

---

## 🎓 Next Steps

Now that ProtonDrive Sync is installed:

1. **Explore the App**
   - Check out all the buttons and options
   - Read the activity log to see what's happening
   - Try manual sync

2. **Configure to Your Needs**
   - Adjust sync interval
   - Set up autostart if desired
   - Organize your sync folder

3. **Learn More**
   - Read about [rclone features](https://rclone.org/commands/)
   - Explore [ProtonDrive capabilities](https://proton.me/drive)
   - Check out the [full README](README.md)

4. **Share Your Experience**
   - Star the project on GitHub ⭐
   - Share with friends who use ProtonDrive
   - Report any issues or suggestions

---

**Made with ❤️ for the Linux and ProtonDrive community**

Happy Syncing! 🚀📁☁️
