# Selective Sync Feature

## Overview

The Selective Sync feature allows you to choose which folders from your ProtonDrive to synchronize locally. This is useful when:
- You have limited local storage space
- You only need access to specific folders
- You want to optimize bandwidth usage
- You need different sync configurations for different devices

## Sync Modes

### 1. Full Sync
Synchronizes all folders from your ProtonDrive to your local directory.

**Use case:** When you want a complete local copy of your ProtonDrive.

### 2. Selective Include
Only synchronizes the folders you explicitly select.

**Use case:** When you want to sync only a few specific folders (e.g., "Work Documents" and "Photos").

**How it works:**
- Start with no folders selected
- Add folders you want to sync
- Only selected folders will be synchronized

### 3. Selective Exclude
Synchronizes all folders except the ones you explicitly exclude.

**Use case:** When you want most of your ProtonDrive but need to skip a few large or unnecessary folders.

**How it works:**
- Start with all folders selected
- Remove folders you don't want to sync
- All folders except excluded ones will be synchronized

## Using Selective Sync

### Initial Setup

1. **Launch the Application:**
   ```bash
   ./run.sh
   ```

2. **Navigate to Sync Settings:**
   - Go to the "Selective Sync" tab in the main window
   - Or use the setup wizard on first run

3. **Choose Your Sync Mode:**
   - Click on the radio button for your preferred mode
   - The folder tree will update to reflect your choice

4. **Select Folders:**
   - **For Include Mode:** Check the folders you want to sync
   - **For Exclude Mode:** Uncheck the folders you don't want to sync
   - The tree shows your ProtonDrive folder structure

5. **View Estimated Size:**
   - Click "Estimate Size" to see how much data will be synced
   - Useful for planning storage requirements

6. **Apply Changes:**
   - Click "Apply Sync Filters"
   - Your selections will be saved to the configuration

### Modifying Your Selection

You can change your folder selection at any time:

1. Open the application
2. Go to "Selective Sync" tab
3. Modify your selections
4. Click "Apply Sync Filters"
5. The next sync will respect your new configuration

## Safety Features

### Dry Run
Before performing a large sync, the application can:
- Show what would be transferred
- Display the estimated data size
- Ask for confirmation before proceeding

**Enable in Settings:**
```
☑ Perform dry run before first sync
```

### Large Sync Warning
If your sync would transfer more than the configured threshold (default: 1GB):
- You'll receive a warning prompt
- You can review the estimated size
- You can choose to proceed or cancel

**Configure in config.json:**
```json
{
  "large_sync_threshold_mb": 1024
}
```

### Bandwidth Limiting
Limit the bandwidth used during sync to avoid network congestion:

**Set in Settings:**
```
Bandwidth Limit: [500] KB/s
```

**Or in config.json:**
```json
{
  "bandwidth_limit_kbps": 500
}
```

## Configuration File

Selective sync settings are stored in `~/.config/protondrive-sync/config.json`:

```json
{
  "sync_mode": "selective_include",
  "included_folders": [
    "Work Documents",
    "Photos/2024"
  ],
  "excluded_folders": [],
  "dry_run_first_sync": true,
  "large_sync_threshold_mb": 1024,
  "bandwidth_limit_kbps": 0
}
```

### Configuration Options

| Option | Values | Description |
|--------|--------|-------------|
| `sync_mode` | `full`, `selective_include`, `selective_exclude` | Determines which folders to sync |
| `included_folders` | List of folder paths | Folders to include (for include mode) |
| `excluded_folders` | List of folder paths | Folders to exclude (for exclude mode) |
| `dry_run_first_sync` | `true`, `false` | Perform dry run before first sync |
| `large_sync_threshold_mb` | Number (MB) | Size threshold for warning prompt |
| `bandwidth_limit_kbps` | Number (KB/s) | Bandwidth limit (0 = unlimited) |

## Technical Details

### Rclone Integration

The selective sync feature uses rclone's filter system:

**Include Mode:**
```bash
rclone sync protondrive: /local/path \
  --include "Work Documents/**" \
  --include "Photos/2024/**" \
  --exclude "*"
```

**Exclude Mode:**
```bash
rclone sync protondrive: /local/path \
  --exclude "Large Videos/**" \
  --exclude "Archive/**"
```

### Folder Listing

The application uses `rclone lsf` to retrieve the folder structure:
```bash
rclone lsf protondrive: --dirs-only --recursive --max-depth 5
```

### Size Estimation

Size calculation uses `rclone size` with filters:
```bash
rclone size protondrive: --include "Selected/**" --json
```

## Troubleshooting

### Problem: Folders not appearing in tree

**Solution:**
1. Verify ProtonDrive is configured:
   ```bash
   rclone listremotes
   ```
2. Check ProtonDrive connection:
   ```bash
   rclone lsd protondrive:
   ```
3. Review application logs for errors

### Problem: Sync includes/excludes wrong folders

**Solution:**
1. Check `config.json` for correct folder paths
2. Verify folder names match exactly (case-sensitive)
3. Use folder browser in application to ensure correct selection
4. Test with dry run to preview changes

### Problem: Size estimation takes too long

**Solution:**
- Large ProtonDrive accounts may take time to scan
- Cancel and proceed if you don't need exact size
- Size estimation is optional

### Problem: First sync is very slow

**Solution:**
1. Check your bandwidth limit setting
2. Verify internet connection speed
3. ProtonDrive API may have rate limits
4. Consider syncing smaller folder sets first

## Best Practices

1. **Start Small:** Begin with a few important folders
2. **Test First:** Use dry run to preview large syncs
3. **Monitor Usage:** Check disk space before major syncs
4. **Regular Review:** Periodically review your folder selection
5. **Bandwidth Control:** Set limits during business hours
6. **Nested Folders:** When including a parent folder, all subfolders are included

## Examples

### Example 1: Sync only work files
```
Mode: Selective Include
Selected:
  ✓ Work Documents
  ✓ Projects/Current
```

### Example 2: Sync everything except large media
```
Mode: Selective Exclude
Excluded:
  ✗ Videos
  ✗ Raw Photos
  ✗ Backup Archives
```

### Example 3: Sync with bandwidth limit
```
Mode: Full
Bandwidth Limit: 500 KB/s
Dry Run: Enabled
```

## See Also

- [ProtonDrive Setup Guide](../setup/PROTONDRIVE_SETUP.md)
- [Authentication Documentation](authentication.md)
- [Installation Guide](../setup/INSTALLATION_GUIDE.md)
