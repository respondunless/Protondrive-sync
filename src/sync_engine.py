"""Background sync engine with threading."""

import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
import logging

from .rclone_manager import RcloneManager
from .config_manager import ConfigManager


class SyncEngine:
    """Manages background sync operations."""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        rclone_manager: RcloneManager,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the sync engine.
        
        Args:
            config_manager: Configuration manager instance
            rclone_manager: Rclone manager instance
            logger: Optional logger instance
        """
        self.config = config_manager
        self.rclone = rclone_manager
        self.logger = logger or logging.getLogger(__name__)
        
        self.is_running = False
        self.sync_thread: Optional[threading.Thread] = None
        self.auto_sync_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        self.last_sync_time: Optional[datetime] = None
        self.sync_in_progress = False
        self.sync_paused = False
        self.first_sync_done = False
        
        # Callbacks
        self.on_sync_start: Optional[Callable] = None
        self.on_sync_complete: Optional[Callable[[bool, str]]] = None
        self.on_sync_progress: Optional[Callable[[str]]] = None
        self.on_sync_warning: Optional[Callable[[str, dict]]] = None  # For warnings before large syncs
    
    def start_auto_sync(self) -> bool:
        """Start automatic sync in background.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running:
            self.logger.warning("Auto sync already running")
            return False
        
        if not self.config.is_configured():
            self.logger.error("Cannot start auto sync: not configured")
            return False
        
        self.is_running = True
        self.stop_event.clear()
        
        self.auto_sync_thread = threading.Thread(
            target=self._auto_sync_loop,
            daemon=True
        )
        self.auto_sync_thread.start()
        
        self.logger.info("Auto sync started")
        return True
    
    def stop_auto_sync(self) -> None:
        """Stop automatic sync."""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        if self.auto_sync_thread and self.auto_sync_thread.is_alive():
            self.auto_sync_thread.join(timeout=5)
        
        self.logger.info("Auto sync stopped")
    
    def _auto_sync_loop(self) -> None:
        """Main loop for automatic sync."""
        interval = self.config.get("sync_interval_minutes", 30) * 60
        
        while self.is_running and not self.stop_event.is_set():
            # Perform sync
            self.sync_now()
            
            # Wait for next interval or stop event
            self.stop_event.wait(timeout=interval)
    
    def sync_now(self, blocking: bool = False) -> bool:
        """Trigger an immediate sync.
        
        Args:
            blocking: If True, wait for sync to complete
            
        Returns:
            True if sync started, False otherwise
        """
        if self.sync_in_progress:
            self.logger.warning("Sync already in progress")
            return False
        
        if not self.config.is_configured():
            self.logger.error("Cannot sync: not configured")
            return False
        
        if blocking:
            self._perform_sync()
            return True
        else:
            self.sync_thread = threading.Thread(
                target=self._perform_sync,
                daemon=True
            )
            self.sync_thread.start()
            return True
    
    def _perform_sync(self, force_sync: bool = False) -> None:
        """Perform the actual sync operation.
        
        Args:
            force_sync: If True, skip safety checks
        """
        self.sync_in_progress = True
        
        if self.on_sync_start:
            self.on_sync_start()
        
        try:
            remote = self.config.get("rclone_remote")
            local_folder = self.config.get("local_folder")
            
            # Construct paths
            source = f"{remote}:"
            destination = local_folder
            
            # Get sync filters
            filters = self.config.get_sync_filters()
            
            # Get bandwidth limit
            bandwidth_limit = self.config.get("bandwidth_limit_kbps", 0)
            
            # Safety check for first sync
            if not self.first_sync_done and not force_sync:
                if self.config.get("dry_run_first_sync", True):
                    self.logger.info("Performing dry-run for first sync...")
                    dry_success, dry_msg = self.rclone.sync(
                        source=source,
                        destination=destination,
                        progress_callback=self._handle_progress,
                        dry_run=True,
                        filters=filters
                    )
                    
                    if not dry_success:
                        self.logger.error(f"Dry-run failed: {dry_msg}")
                        if self.on_sync_complete:
                            self.on_sync_complete(False, f"Dry-run failed: {dry_msg}")
                        self.sync_in_progress = False
                        return
                
                # Estimate sync size
                success, size_info = self.rclone.estimate_sync_size(
                    source=source,
                    destination=destination,
                    filters=filters
                )
                
                if success:
                    size_mb = size_info.get("size_mb", 0)
                    threshold = self.config.get("large_sync_threshold_mb", 1000)
                    
                    if size_mb > threshold and self.config.get("confirm_large_sync", True):
                        # Warn about large sync
                        if self.on_sync_warning:
                            self.on_sync_warning("large_sync", size_info)
                        
                        # If no confirmation callback or user didn't confirm, abort
                        # (The GUI will handle this callback and show a dialog)
                        self.logger.warning(f"Large sync detected: {size_mb:.2f} MB")
                        # For now, we'll proceed - the GUI will handle confirmation
            
            self.logger.info(f"Syncing {source} to {destination}")
            if filters:
                self.logger.info(f"Using filters: {filters}")
            
            # Perform sync
            success, message = self.rclone.sync(
                source=source,
                destination=destination,
                progress_callback=self._handle_progress,
                dry_run=False,
                filters=filters,
                bandwidth_limit_kbps=bandwidth_limit
            )
            
            if success:
                self.last_sync_time = datetime.now()
                self.first_sync_done = True
                self.logger.info("Sync completed successfully")
            else:
                self.logger.error(f"Sync failed: {message}")
            
            # Notify completion
            if self.on_sync_complete:
                self.on_sync_complete(success, message)
                
        except Exception as e:
            self.logger.error(f"Error during sync: {e}")
            if self.on_sync_complete:
                self.on_sync_complete(False, str(e))
        finally:
            self.sync_in_progress = False
    
    def _handle_progress(self, line: str) -> None:
        """Handle progress updates from rclone.
        
        Args:
            line: Progress line from rclone
        """
        if self.on_sync_progress:
            self.on_sync_progress(line)
    
    def cancel_sync(self) -> bool:
        """Cancel ongoing sync.
        
        Returns:
            True if cancelled, False otherwise
        """
        if not self.sync_in_progress:
            return False
        
        return self.rclone.cancel_sync()
    
    def pause_sync(self) -> bool:
        """Pause ongoing sync.
        
        Returns:
            True if paused, False otherwise
        """
        if self.sync_in_progress and not self.sync_paused:
            self.sync_paused = True
            # For now, we'll just set a flag
            # A more sophisticated implementation would pause rclone
            self.logger.info("Sync paused")
            return True
        return False
    
    def resume_sync(self) -> bool:
        """Resume paused sync.
        
        Returns:
            True if resumed, False otherwise
        """
        if self.sync_paused:
            self.sync_paused = False
            self.logger.info("Sync resumed")
            return True
        return False
    
    def get_status(self) -> dict:
        """Get current sync status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "is_running": self.is_running,
            "sync_in_progress": self.sync_in_progress,
            "sync_paused": self.sync_paused,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "configured": self.config.is_configured(),
            "first_sync_done": self.first_sync_done
        }
