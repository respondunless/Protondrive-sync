# ProtonDrive Authentication

## Overview

This application uses **rclone** to authenticate with ProtonDrive. Rclone is a powerful command-line tool that handles the authentication flow securely.

## Authentication Methods

ProtonDrive supports two authentication methods through rclone:

### 1. Standard Login (Username + Password)
- Your regular ProtonMail email and password
- Recommended for accounts without 2FA
- Simplest setup process

### 2. Two-Factor Authentication (2FA)
- Required if you have 2FA enabled on your Proton account
- Uses app-specific passwords
- More secure for sensitive data

## Setup Process

### First-Time Configuration

The application provides a guided setup wizard:

1. **Launch Setup:**
   ```bash
   ./run.sh
   ```
   - The wizard appears automatically on first run
   - Or manually trigger via "Configure ProtonDrive" button

2. **Rclone Configuration Opens:**
   - A terminal window launches automatically
   - You'll see the rclone interactive configuration

3. **Follow Rclone Prompts:**
   ```
   n) New remote
   name> protondrive
   Storage> protondrive
   ```

4. **Enter Credentials:**
   - **If no 2FA:** Enter username and password
   - **If 2FA enabled:** See section below

5. **Verify Connection:**
   - The application will test the connection
   - You'll see a success message when ready

### Authentication with 2FA

If you have Two-Factor Authentication enabled:

#### Step 1: Generate App Password

1. **Log into ProtonMail web interface**
2. **Navigate to Settings:**
   - Click on your profile (top-right)
   - Go to "Account" → "Security"

3. **Create App Password:**
   - Find "App passwords" section
   - Click "Create app password"
   - Give it a name (e.g., "Rclone Sync")
   - Copy the generated password

4. **Save Securely:**
   - Store in a password manager
   - You cannot view it again after closing

#### Step 2: Use App Password in Rclone

```
Username: your-email@protonmail.com
Password: [paste app password here]
```

**Important:** Use the app password, NOT your regular password!

## Security Considerations

### Password Storage

Rclone stores credentials securely:

**Location:**
```
~/.config/rclone/rclone.conf
```

**Encryption:**
- Passwords are obscured by default
- For additional security, use rclone's password encryption:
  ```bash
  rclone config password
  ```

**Permissions:**
```bash
chmod 600 ~/.config/rclone/rclone.conf
```

### Best Practices

1. **Use App Passwords:**
   - Even if 2FA is optional, app passwords are more secure
   - Allows revocation without changing main password
   - Limits scope of access

2. **Enable 2FA:**
   - Protect your Proton account with 2FA
   - Prevents unauthorized access
   - Use TOTP apps (Authy, Google Authenticator, etc.)

3. **Secure Configuration:**
   - Keep rclone.conf file private
   - Don't share or commit to version control
   - Back up securely (encrypted)

4. **Regular Review:**
   - Periodically check active app passwords
   - Revoke unused passwords
   - Update if compromised

5. **Network Security:**
   - Use trusted networks
   - Consider VPN for public Wi-Fi
   - All ProtonDrive traffic is encrypted

## Troubleshooting Authentication

### Problem: Login fails with correct credentials

**Possible causes:**
- 2FA is enabled but using regular password
- App password expired or revoked
- Account locked or suspended

**Solutions:**
1. Verify 2FA status in Proton account
2. Generate new app password
3. Check Proton account status
4. Test login on ProtonMail web interface

### Problem: Terminal doesn't open for configuration

**Solutions:**
1. **Manual configuration:**
   ```bash
   rclone config
   ```
2. **Check terminal emulator:**
   ```bash
   which gnome-terminal konsole xterm
   ```
3. **Install terminal:**
   ```bash
   # Arch/CachyOS
   sudo pacman -S gnome-terminal
   
   # Ubuntu/Debian
   sudo apt install gnome-terminal
   ```

### Problem: "No remotes found" error

**Solutions:**
1. Run configuration wizard again
2. Manually configure rclone:
   ```bash
   rclone config
   ```
3. Verify remote exists:
   ```bash
   rclone listremotes
   ```

### Problem: Authentication works but can't list files

**Possible causes:**
- Network connectivity issues
- ProtonDrive API temporary outage
- Rate limiting

**Solutions:**
1. Check internet connection
2. Verify ProtonDrive web access
3. Wait a few minutes and retry
4. Check rclone verbose output:
   ```bash
   rclone lsd protondrive: -vv
   ```

## Manual Rclone Configuration

If the wizard doesn't work, configure manually:

### Step-by-Step Manual Setup

1. **Open terminal:**
   ```bash
   rclone config
   ```

2. **Create new remote:**
   ```
   n) New remote
   name> protondrive
   ```

3. **Select ProtonDrive:**
   ```
   Storage> protondrive
   ```
   (Type the number corresponding to ProtonDrive)

4. **Enter username:**
   ```
   username> your-email@protonmail.com
   ```

5. **Enter password:**
   ```
   password> [your-password-or-app-password]
   ```

6. **Configure advanced options (optional):**
   ```
   Edit advanced config? (y/n)
   n
   ```

7. **Save configuration:**
   ```
   y) Yes this is OK
   q) Quit config
   ```

8. **Test connection:**
   ```bash
   rclone lsd protondrive:
   ```

## Reconfiguring Authentication

To update credentials or reconfigure:

### Method 1: Application Interface
1. Open the application
2. Go to "Settings" tab
3. Click "Configure ProtonDrive"
4. Follow the wizard

### Method 2: Command Line
```bash
rclone config reconnect protondrive:
```

### Method 3: Complete Reconfiguration
```bash
rclone config delete protondrive
rclone config
```

## Environment Variables

For automated setups, you can use environment variables:

```bash
export RCLONE_CONFIG_PROTONDRIVE_TYPE=protondrive
export RCLONE_CONFIG_PROTONDRIVE_USERNAME=your-email@protonmail.com
export RCLONE_CONFIG_PROTONDRIVE_PASSWORD=your-app-password
```

**Warning:** Be cautious with passwords in environment variables!

## Token Refresh

ProtonDrive authentication tokens:
- Are managed automatically by rclone
- Refresh before expiration
- Should not require manual intervention

If you experience frequent authentication prompts:
1. Check system clock accuracy
2. Verify internet stability
3. Consider recreating the remote

## Multi-Account Support

To use multiple ProtonDrive accounts:

1. **Create additional remotes:**
   ```bash
   rclone config
   # Create: protondrive-personal, protondrive-work, etc.
   ```

2. **Configure application:**
   - Edit `~/.config/protondrive-sync/config.json`
   - Change `remote_name` to desired remote

3. **Or run multiple instances:**
   - Use different configuration directories
   - Set `XDG_CONFIG_HOME` environment variable

## See Also

- [ProtonDrive Setup Guide](../setup/PROTONDRIVE_SETUP.md)
- [Selective Sync Documentation](selective-sync.md)
- [Rclone Official Documentation](https://rclone.org/protondrive/)
- [Proton Account Security Settings](https://account.proton.me/security)
