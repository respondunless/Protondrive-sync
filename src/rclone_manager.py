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
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """Perform sync operation.
        
        Args:
            source: Source path (remote:path or local path)
            destination: Destination path (remote:path or local path)
            progress_callback: Optional callback for progress updates
            dry_run: If True, perform a dry run
            
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
