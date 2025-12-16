# Migration Guide: V1 to V2 (Modern Wizard)

## What's Changed?

ProtonDrive Sync V2 introduces a **Modern ProtonDrive Authentication Wizard** that replaces the terminal-based `rclone config` interface with a sleek, user-friendly GUI.

## For Existing Users

### ✅ **Good News: Existing Configurations Work!**

If you already have ProtonDrive configured with the old terminal-based method, **you don't need to reconfigure anything**. The new version will automatically detect your existing configuration and use it.

### 🔄 **What Happens on Upgrade**

When you upgrade to V2:

1. **Existing Remote Detected**: The setup wizard will detect your existing ProtonDrive remote
2. **Skip Reconfiguration**: You can skip the ProtonDrive setup page
3. **Continue Setup**: Proceed with selecting sync folders and preferences

### 🆕 **Want to Try the New Wizard?**

If you want to experience the new modern wizard or need to reconfigure:

1. **Option 1: Delete Old Remote (Manual)**
   ```bash
   rclone config delete protondrive
   ```
   Then restart the app and use the new wizard.

2. **Option 2: Use Different Remote Name**
   - In the new wizard, choose a different name (e.g., "protondrive2")
   - Configure with the modern interface
   - Update your sync settings to use the new remote

3. **Option 3: Replace via Wizard**
   - Start the new wizard
   - Use the same remote name
   - The wizard will ask if you want to replace the existing configuration
   - Click "Yes" to reconfigure with the modern interface

## For New Users

### 🎉 **You Get the Best Experience!**

As a new user, you'll automatically use the Modern ProtonDrive Wizard:

1. **First Launch**: The setup wizard appears
2. **Authentication Page**: Click "Configure ProtonDrive Now"
3. **Modern Wizard Opens**: Fill in your credentials in the beautiful GUI
4. **Automatic Configuration**: Everything is set up for you
5. **Done**: Proceed to folder selection and sync settings

## Key Improvements in V2

### **Before (V1) vs After (V2)**

| Feature | V1 (Terminal) | V2 (Modern Wizard) |
|---------|---------------|-------------------|
| **Interface** | Text-based terminal | Modern graphical dialog |
| **Provider Selection** | Scroll through 64+ options | Pre-selected ProtonDrive |
| **Credential Entry** | Text prompts | Clean input fields with labels |
| **Password Visibility** | Hidden (no toggle) | Show/hide toggle |
| **2FA Input** | Confusing prompt | Clear field with explanation |
| **Progress Feedback** | None | Real-time progress bar |
| **Error Messages** | Technical | User-friendly |
| **Time to Configure** | 2-5 minutes | 30 seconds |

## Compatibility

### **Fully Compatible**
- ✅ Existing rclone configurations
- ✅ All sync modes (full, selective, exclude)
- ✅ All settings and preferences
- ✅ Log files and history
- ✅ System tray functionality

### **No Breaking Changes**
- ✅ Config file format unchanged
- ✅ rclone backend unchanged
- ✅ Sync engine unchanged
- ✅ File locations unchanged

## Troubleshooting

### **"I can't see the new wizard"**

**Cause**: You already have ProtonDrive configured

**Solution**: The wizard only appears if ProtonDrive is not configured. To see it:
1. Delete your existing remote: `rclone config delete protondrive`
2. Restart the application
3. The new wizard will appear

### **"My existing setup stopped working"**

**Cause**: Unlikely, but possible configuration conflict

**Solution**:
1. Check your rclone configuration: `rclone listremotes`
2. Test your remote: `rclone lsd protondrive:`
3. If issues persist, reconfigure using the new wizard
4. Check logs: `~/.config/protondrive-sync/protondrive-sync.log`

### **"I prefer the terminal interface"**

**Solution**: You can still use the terminal interface:
```bash
rclone config
```
The app will detect and use any valid ProtonDrive remote, regardless of how it was configured.

## Upgrade Steps

### **Step-by-Step Upgrade Process**

1. **Backup Your Configuration** (Recommended)
   ```bash
   cp ~/.config/protondrive-sync/config.json ~/.config/protondrive-sync/config.json.backup
   cp ~/.config/rclone/rclone.conf ~/.config/rclone/rclone.conf.backup
   ```

2. **Pull Latest Changes**
   ```bash
   cd protondrive-sync
   git pull origin main
   ```

3. **Install Dependencies** (if needed)
   ```bash
   pip install -r requirements.txt --upgrade
   ```

4. **Restart Application**
   ```bash
   python -m protondrive_sync.main
   ```

5. **Verify Everything Works**
   - Check that your sync settings are intact
   - Verify that auto-sync is still working
   - Test a manual sync

## Rollback (If Needed)

If you encounter issues and need to rollback:

1. **Restore Configuration Backups**
   ```bash
   cp ~/.config/protondrive-sync/config.json.backup ~/.config/protondrive-sync/config.json
   cp ~/.config/rclone/rclone.conf.backup ~/.config/rclone/rclone.conf
   ```

2. **Checkout Previous Version**
   ```bash
   cd protondrive-sync
   git checkout <previous-commit-hash>
   ```

3. **Restart Application**

## Support

If you encounter any issues during migration:

1. **Check Logs**: `~/.config/protondrive-sync/protondrive-sync.log`
2. **Report Issues**: Open a GitHub issue with details
3. **Community Help**: Ask in discussions or forums

## Frequently Asked Questions

### **Q: Do I need to reconfigure if I upgrade?**
A: No, existing configurations work perfectly.

### **Q: Can I use both terminal and GUI configuration?**
A: Yes, but it's recommended to use one method for consistency.

### **Q: Will my sync history be preserved?**
A: Yes, all sync history and logs are preserved.

### **Q: Is the new wizard more secure?**
A: Yes, credentials are handled the same way as rclone (never stored in plain text).

### **Q: Can I switch back to terminal configuration?**
A: Yes, you can always use `rclone config` directly if preferred.

### **Q: Does the new wizard support all rclone ProtonDrive options?**
A: It supports the most common options. Advanced options can still be configured via `rclone config`.

---

**Welcome to ProtonDrive Sync V2!** 🎉

Enjoy the new modern authentication experience!
