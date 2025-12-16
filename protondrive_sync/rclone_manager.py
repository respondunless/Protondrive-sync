"""Rclone integration and command execution."""

import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Callable
import logging


class RcloneManager:
    """Manages rclone operations."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the rclone manager.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.process: Optional[subprocess.Popen] = None
    
    def is_installed(self) -> bool:
        """Check if rclone is installed.
        
        Returns:
            True if rclone is installed, False otherwise
        """
        return shutil.which("rclone") is not None
    
    def get_version(self) -> Optional[str]:
        """Get rclone version.
        
        Returns:
            Version string or None if error
        """
        try:
            result = subprocess.run(
                ["rclone", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Extract version from first line
                first_line = result.stdout.split('\n')[0]
                match = re.search(r'v([\d.]+)', first_line)
                if match:
                    return match.group(1)
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Error getting rclone version: {e}")
            return None
    
    def list_remotes(self) -> List[str]:
        """List all configured rclone remotes.
        
        Returns:
            List of remote names
        """
        try:
            result = subprocess.run(
                ["rclone", "listremotes"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Remove trailing colons and filter empty lines
                remotes = [line.rstrip(':') for line in result.stdout.strip().split('\n') if line]
                return remotes
            else:
                self.logger.error(f"Error listing remotes: {result.stderr}")
                return []
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Error listing remotes: {e}")
            return []
    
    def remote_exists(self, remote_name: str) -> bool:
        """Check if a remote exists.
        
        Args:
            remote_name: Name of the remote
            
        Returns:
            True if remote exists, False otherwise
        """
        remotes = self.list_remotes()
        return remote_name in remotes
    
    def test_remote(self, remote_name: str) -> Tuple[bool, str]:
        """Test if a remote is accessible.
        
        Args:
            remote_name: Name of the remote
            
        Returns:
            Tuple of (success, message)
        """
        try:
            result = subprocess.run(
                ["rclone", "lsd", f"{remote_name}:", "--max-depth", "1"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, "Remote is accessible"
            else:
                return False, f"Error: {result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return False, "Timeout while testing remote"
        except FileNotFoundError:
            return False, "Rclone not found"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def sync(
        self,
        source: str,
        destination: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        dry_run: bool = False,
        filters: Optional[List[str]] = None,
        bandwidth_limit_kbps: int = 0
    ) -> Tuple[bool, str]:
        """Perform sync operation.
        
        Args:
            source: Source path (remote:path or local path)
            destination: Destination path (remote:path or local path)
            progress_callback: Optional callback for progress updates
            dry_run: If True, perform a dry run
            filters: Optional list of rclone filter arguments
            bandwidth_limit_kbps: Bandwidth limit in KB/s (0 = no limit)
            
        Returns:
            Tuple of (success, message)
        """
        cmd = [
            "rclone", "sync",
            source,
            destination,
            "--progress",
            "--stats", "1s",
            "-v"
        ]
        
        if dry_run:
            cmd.append("--dry-run")
        
        if filters:
            cmd.extend(filters)
        
        if bandwidth_limit_kbps > 0:
            cmd.extend(["--bwlimit", f"{bandwidth_limit_kbps}k"])
        
        try:
            self.logger.info(f"Starting sync: {source} -> {destination}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            output_lines = []
            
            # Read output line by line
            if self.process.stdout:
                for line in iter(self.process.stdout.readline, ''):
                    line = line.strip()
                    if line:
                        output_lines.append(line)
                        self.logger.debug(line)
                        if progress_callback:
                            progress_callback(line)
            
            # Wait for process to complete
            return_code = self.process.wait()
            self.process = None
            
            full_output = '\n'.join(output_lines)
            
            if return_code == 0:
                self.logger.info("Sync completed successfully")
                return True, "Sync completed successfully"
            else:
                error_msg = f"Sync failed with return code {return_code}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except FileNotFoundError:
            error_msg = "Rclone not found. Please install rclone."
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error during sync: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def cancel_sync(self) -> bool:
        """Cancel ongoing sync operation.
        
        Returns:
            True if cancelled, False otherwise
        """
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.logger.info("Sync cancelled")
                return True
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.logger.warning("Sync force killed")
                return True
            except Exception as e:
                self.logger.error(f"Error cancelling sync: {e}")
                return False
        return False
    
    def is_syncing(self) -> bool:
        """Check if a sync operation is in progress.
        
        Returns:
            True if syncing, False otherwise
        """
        return self.process is not None and self.process.poll() is None
    
    def get_remote_type(self, remote_name: str) -> Optional[str]:
        """Get the type of a remote (e.g., 'protondrive', 's3', 'drive').
        
        Args:
            remote_name: Name of the remote
            
        Returns:
            Remote type string or None if error
        """
        try:
            result = subprocess.run(
                ["rclone", "config", "show", remote_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse the config to find type
                for line in result.stdout.split('\n'):
                    if line.strip().startswith('type ='):
                        return line.split('=')[1].strip()
            return None
        except Exception as e:
            self.logger.error(f"Error getting remote type: {e}")
            return None
    
    def has_protondrive_remote(self) -> Tuple[bool, Optional[str]]:
        """Check if any ProtonDrive remote is configured.
        
        Returns:
            Tuple of (has_protondrive, remote_name)
        """
        remotes = self.list_remotes()
        for remote in remotes:
            remote_type = self.get_remote_type(remote)
            if remote_type and 'proton' in remote_type.lower():
                return True, remote
        return False, None
    
    def list_folders(self, remote_name: str, path: str = "") -> List[Dict[str, str]]:
        """List folders in a remote path.
        
        Args:
            remote_name: Name of the remote
            path: Path within the remote (empty string for root)
            
        Returns:
            List of dictionaries with folder info (name, path, size, modtime)
        """
        try:
            remote_path = f"{remote_name}:{path}"
            result = subprocess.run(
                ["rclone", "lsf", remote_path, "--dirs-only", "--format", "p"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                folders = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        # Remove trailing slash
                        folder_name = line.rstrip('/')
                        full_path = f"{path}/{folder_name}" if path else folder_name
                        folders.append({
                            "name": folder_name,
                            "path": full_path,
                            "full_path": f"{remote_name}:{full_path}"
                        })
                return folders
            else:
                self.logger.error(f"Error listing folders: {result.stderr}")
                return []
        except Exception as e:
            self.logger.error(f"Error listing folders: {e}")
            return []
    
    def get_folder_tree(self, remote_name: str, max_depth: int = 3) -> List[Dict[str, any]]:
        """Get a tree structure of folders in the remote.
        
        Args:
            remote_name: Name of the remote
            max_depth: Maximum depth to traverse
            
        Returns:
            List of folder dictionaries with nested children
        """
        def build_tree(path: str = "", depth: int = 0):
            if depth >= max_depth:
                return []
            
            folders = self.list_folders(remote_name, path)
            result = []
            
            for folder in folders:
                folder_item = {
                    "name": folder["name"],
                    "path": folder["path"],
                    "full_path": folder["full_path"],
                    "children": build_tree(folder["path"], depth + 1)
                }
                result.append(folder_item)
            
            return result
        
        return build_tree()
    
    def estimate_sync_size(
        self,
        source: str,
        destination: str,
        filters: Optional[List[str]] = None
    ) -> Tuple[bool, Dict[str, any]]:
        """Estimate the size of data that would be synced.
        
        Args:
            source: Source path
            destination: Destination path
            filters: Optional list of rclone filter arguments
            
        Returns:
            Tuple of (success, stats_dict)
        """
        cmd = [
            "rclone", "size",
            source,
            "--json"
        ]
        
        if filters:
            cmd.extend(filters)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                import json
                stats = json.loads(result.stdout)
                return True, {
                    "bytes": stats.get("bytes", 0),
                    "count": stats.get("count", 0),
                    "size_mb": stats.get("bytes", 0) / (1024 * 1024),
                    "size_gb": stats.get("bytes", 0) / (1024 * 1024 * 1024)
                }
            else:
                self.logger.error(f"Error estimating size: {result.stderr}")
                return False, {}
        except Exception as e:
            self.logger.error(f"Error estimating size: {e}")
            return False, {}
    
    def configure_protondrive(self) -> Tuple[bool, str]:
        """Launch interactive ProtonDrive configuration.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Launch rclone config in a terminal
            import os
            
            # Try different terminal emulators
            terminals = [
                ['x-terminal-emulator', '-e'],
                ['gnome-terminal', '--'],
                ['konsole', '-e'],
                ['xfce4-terminal', '-e'],
                ['xterm', '-e'],
                ['alacritty', '-e'],
                ['kitty', '-e']
            ]
            
            for term in terminals:
                try:
                    subprocess.Popen(term + ['rclone', 'config'])
                    return True, "rclone config launched in terminal"
                except FileNotFoundError:
                    continue
            
            return False, "Could not find a terminal emulator to launch rclone config"
            
        except Exception as e:
            return False, f"Error launching rclone config: {str(e)}"
