# 🔐 ProtonDrive Setup Guide

This guide will help you set up ProtonDrive with rclone for use with ProtonDrive Sync.

---

## 📋 Prerequisites

Before you begin, make sure you have:

1. **ProtonDrive Account** (Free or Paid plan)
   - Sign up at [proton.me/drive](https://proton.me/drive) if you don't have one
   - ProtonDrive Sync works with both free and paid accounts

2. **ProtonDrive Password** 
   - Your regular Proton account password
   - Keep it handy for the setup process

3. **2FA Code** (if enabled)
   - If you have two-factor authentication enabled on your Proton account
   - Have your 2FA device (phone/authenticator app) ready

4. **rclone installed**
   - Should already be installed if you used our installer
   - Verify with: `rclone version`

---

## 🚀 Quick Setup (Recommended)

The easiest way to set up ProtonDrive is through the built-in setup wizard:

1. **Launch ProtonDrive Sync**
   ```bash
   protondrive-sync
   ```

2. **Follow the Setup Wizard**
   - The wizard will detect if ProtonDrive is configured
   - If not, click **"Configure ProtonDrive Now"**
   - A terminal window will open automatically

3. **Complete Configuration**
   - Follow the on-screen instructions
   - The wizard will test your connection
   - Once successful, proceed to selective sync and other settings

---

## 🔧 Manual Setup (Advanced)

If you prefer to configure rclone manually or the automatic method didn't work:

### Step 1: Open rclone Configuration

Open a terminal and run:

```bash
rclone config
```

### Step 2: Create New Remote

When prompted:

```
Current remotes:

Name                 Type
====                 ====

e) Edit existing remote
n) New remote
d) Delete remote
r) Rename remote
c) Copy remote
s) Set configuration password
q) Quit config
```

Type **`n`** and press Enter.

### Step 3: Name Your Remote

```
Enter name for new remote.
name>
```

Type a name like **`protondrive`** (or any name you prefer) and press Enter.

### Step 4: Select ProtonDrive

You'll see a long list of storage providers:

```
Type of storage to configure.
Choose a number from below, or type in your own value
[...]
35 / Proton Drive
   \ (protondrive)
[...]
```

Find **"Proton Drive"** in the list (usually number 35 or nearby) and enter that number.

### Step 5: Configure ProtonDrive Settings

#### Username (Email)
```
Proton Drive username (email).
Enter a value.
username>
```
Enter your **ProtonDrive email address**.

#### Password
```
Proton Drive password.
Enter a value.
password>
```
Enter your **ProtonDrive password**.

**⚠️ Security Note:** Your password is stored securely by rclone using encryption.

#### 2FA (If Enabled)
If you have 2FA enabled, you'll be prompted:
```
Proton Drive 2FA code (if enabled).
Enter a value. Press Enter to leave empty.
2fa>
```
Enter your current 2FA code from your authenticator app.

#### App Password (Optional)
For enhanced security, ProtonDrive may ask you to use an app password:
```
Use app password instead of regular password?
Enter a boolean value (true or false). Press Enter for the default (false).
use_app_password>
```

- Type **`false`** for regular password (easier)
- Type **`true`** if you want to use an app-specific password (more secure)

If you choose true, you'll need to:
1. Go to [account.proton.me/security](https://account.proton.me/security)
2. Create an app password for "ProtonDrive Sync"
3. Use that password in the config

### Step 6: Advanced Configuration

```
Edit advanced config?
y/n>
```

Type **`n`** (No) unless you have specific requirements.

### Step 7: Verify Configuration

rclone will show a summary:
```
Configuration complete.
Options:
- type: protondrive
- username: your.email@proton.me
Keep this "protondrive" remote?
y/e/d>
```

Type **`y`** (Yes) to save.

### Step 8: Exit Configuration

```
q) Quit config
```

Type **`q`** to quit.

---

## ✅ Verify Your Setup

Test your ProtonDrive connection:

```bash
rclone lsd protondrive:
```

If successful, you should see a list of your top-level ProtonDrive folders.

**Example output:**
```
          -1 2024-01-15 10:30:45        -1 Documents
          -1 2024-01-15 10:30:45        -1 Photos
          -1 2024-01-15 10:30:45        -1 Work
```

---

## 🎯 Using ProtonDrive with ProtonDrive Sync

Once configured:

1. **Launch ProtonDrive Sync**
   ```bash
   protondrive-sync
   ```

2. **The app will automatically detect** your ProtonDrive remote

3. **Configure sync settings:**
   - Choose sync mode (full/selective/exclude)
   - Select local folder
   - Set up automatic sync

4. **Start syncing!** 🎉

---

## 🛠️ Troubleshooting

### Issue: "Command not found: rclone"

**Solution:**
```bash
# On CachyOS/Arch:
sudo pacman -S rclone

# On Ubuntu/Debian:
sudo apt install rclone

# On Fedora:
sudo dnf install rclone
```

### Issue: "Authentication failed"

**Solutions:**

1. **Check your password** - Make sure you're using the correct ProtonDrive password
2. **2FA code** - If you have 2FA, make sure you entered the current code
3. **Account locked** - Check if your Proton account is locked or requires verification
4. **Reconfigure** - Delete the remote and start over:
   ```bash
   rclone config delete protondrive
   rclone config
   ```

### Issue: "Could not list ProtonDrive folders"

**Solutions:**

1. **Test connection:**
   ```bash
   rclone lsd protondrive: -vv
   ```
   The `-vv` flag shows detailed output for debugging.

2. **Check ProtonDrive status** - Visit [protonstatus.com](https://protonstatus.com) to check if ProtonDrive is experiencing issues

3. **Update rclone:**
   ```bash
   # On CachyOS/Arch:
   sudo pacman -Syu rclone
   ```

4. **Check firewall** - Make sure your firewall isn't blocking rclone

### Issue: "Timeout connecting to ProtonDrive"

**Solutions:**

1. **Check internet connection**
2. **Try again later** - ProtonDrive servers might be busy
3. **Use a different network** - Try switching from WiFi to Ethernet or vice versa
4. **Increase timeout:**
   ```bash
   rclone lsd protondrive: --timeout 60s
   ```

### Issue: "Remote 'protondrive' not found"

**Solution:**

The remote name doesn't match. Check available remotes:
```bash
rclone listremotes
```

Make sure you're using the exact name (case-sensitive) when configuring ProtonDrive Sync.

---

## 🔐 Security Best Practices

### 1. Use App Passwords (Recommended)

Instead of your main ProtonDrive password, create an app-specific password:

1. Go to [account.proton.me/security](https://account.proton.me/security)
2. Scroll to "App passwords"
3. Click "Create app password"
4. Name it "ProtonDrive Sync"
5. Use this password in rclone config

**Benefits:**
- More secure - separate from your main password
- Can be revoked if compromised
- Limited scope

### 2. Enable rclone Configuration Password

Protect your rclone configuration with encryption:

```bash
rclone config
# Choose: s) Set configuration password
```

This encrypts your stored ProtonDrive credentials.

### 3. Secure Your Config File

The rclone config file is located at:
```
~/.config/rclone/rclone.conf
```

Make sure it has restricted permissions:
```bash
chmod 600 ~/.config/rclone/rclone.conf
```

---

## 💡 Tips for CachyOS Users

### Optimized Performance

CachyOS's performance optimizations will benefit ProtonDrive Sync:

- **Faster sync operations** - CachyOS's optimized kernel helps with I/O
- **Better multi-threading** - Parallel operations work more efficiently
- **Lower latency** - Network operations are optimized

### Recommended Settings for CachyOS

1. **Enable automatic sync** - Take advantage of background performance
2. **Use selective sync** - Sync only what you need
3. **Set bandwidth limits** - Prevent network saturation during gaming/streaming
4. **Use SSD for local folder** - If you have one, use it for the sync folder

### AUR Helpers

If you need additional packages:

```bash
# Install yay (recommended)
sudo pacman -S yay

# Or paru
sudo pacman -S paru
```

---

## 📚 Additional Resources

- **rclone Documentation:** [rclone.org/protondrive](https://rclone.org/protondrive/)
- **ProtonDrive Help:** [proton.me/support/drive](https://proton.me/support/drive)
- **ProtonDrive Sync GitHub:** Issues and discussions
- **Proton Community:** [proton.me/community](https://proton.me/community)

---

## ❓ Frequently Asked Questions

### Q: Can I sync multiple ProtonDrive accounts?

**A:** Yes! Create multiple remotes with different names:
```bash
rclone config
# Create: protondrive1, protondrive2, etc.
```

Then in ProtonDrive Sync, you can switch between them in settings.

### Q: Will this work with ProtonDrive free plan?

**A:** Yes! ProtonDrive Sync works with both free and paid plans. Free plan limitations still apply (storage space).

### Q: How secure is this?

**A:** Very secure! 
- Uses ProtonDrive's end-to-end encryption
- rclone securely stores credentials
- All traffic is encrypted
- Open-source code you can audit

### Q: Can I use ProtonDrive Sync on multiple computers?

**A:** Yes! Just configure rclone on each computer. Be careful with bidirectional sync to avoid conflicts.

### Q: Will this sync in real-time?

**A:** Not quite real-time, but you can set sync intervals as low as 5 minutes for near-real-time syncing.

### Q: Does this work offline?

**A:** No, you need an internet connection to sync with ProtonDrive. Local files remain accessible offline.

---

## 🎉 Success!

You're all set up! Your ProtonDrive is now connected and ready to sync.

**Next steps:**
1. Open ProtonDrive Sync
2. Configure your sync preferences
3. Choose which folders to sync
4. Start syncing!

Enjoy secure, private cloud storage with ProtonDrive! 🚀🔐

---

**Need help?** Open an issue on GitHub or check our troubleshooting guide.
