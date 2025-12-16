"""Main entry point for ProtonDrive Sync application."""

import sys
import signal
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
import logging

from .config_manager import ConfigManager
from .rclone_manager import RcloneManager
from .sync_engine import SyncEngine
from .gui import MainWindow, EnhancedSetupWizard
from .tray import SystemTray
from .utils import setup_logging


class ProtonDriveSyncApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        # Setup logging
        log_dir = Path.home() / ".config" / "protondrive-sync"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "protondrive-sync.log"
        
        self.logger = setup_logging("INFO", log_file)
        self.logger.info("=" * 50)
        self.logger.info("ProtonDrive Sync starting...")
        
        # Initialize components
        self.config = ConfigManager()
        self.rclone = RcloneManager(self.logger)
        self.sync_engine = SyncEngine(self.config, self.rclone, self.logger)
        
        # Check rclone installation
        if not self.rclone.is_installed():
            self.logger.error("Rclone is not installed")
            QMessageBox.critical(
                None,
                "Rclone Not Found",
                "Rclone is not installed. Please install rclone first.\n\n"
                "On Arch/CachyOS, run:\n"
                "sudo pacman -S rclone\n\n"
                "Then configure ProtonDrive with:\n"
                "rclone config"
            )
            sys.exit(1)
        
        version = self.rclone.get_version()
        self.logger.info(f"Rclone version: {version}")
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("ProtonDrive Sync")
        self.app.setQuitOnLastWindowClosed(False)  # Keep running in tray
        
        # Create main window
        self.main_window = MainWindow(
            self.config,
            self.rclone,
            self.sync_engine,
            self.logger
        )
        
        # Create system tray
        self.tray = SystemTray(
            self.config,
            self.sync_engine,
            self.logger
        )
        
        # Connect signals
        self.tray.show_window.connect(self.show_main_window)
        self.tray.quit_app.connect(self.quit_application)
        self.main_window.show_notification.connect(self.show_notification)
        
        # Setup status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_tray_status)
        self.status_timer.start(2000)  # Update every 2 seconds
        
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Timer to allow Ctrl+C to work
        self.timer = QTimer()
        self.timer.start(500)
        self.timer.timeout.connect(lambda: None)
    
    def run(self):
        """Run the application."""
        # Show setup wizard on first run
        if self.config.is_first_run() or not self.config.is_configured():
            self.logger.info("First run detected, showing setup wizard")
            wizard = EnhancedSetupWizard(self.config, self.rclone)
            
            if wizard.exec_() != wizard.Accepted:
                self.logger.info("Setup cancelled by user")
                return 0
            
            self.logger.info("Setup completed")
        
        # Start auto-sync if enabled
        if self.config.get("auto_sync_enabled", False):
            self.logger.info("Starting auto-sync")
            self.sync_engine.start_auto_sync()
            self.tray.update_menu_state(True)
        
        # Show main window
        self.main_window.show()
        
        # Show welcome notification
        self.tray.show_message(
            "ProtonDrive Sync",
            "Application started. Click the tray icon to access controls."
        )
        
        # Start event loop
        return self.app.exec_()
    
    def show_main_window(self):
        """Show the main window."""
        self.main_window.show()
        self.main_window.activateWindow()
        self.main_window.raise_()
    
    def show_notification(self, title: str, message: str):
        """Show notification via system tray."""
        self.tray.show_message(title, message)
    
    def update_tray_status(self):
        """Update tray icon status."""
        status = self.sync_engine.get_status()
        
        if status['sync_in_progress']:
            self.tray.update_status("Syncing...")
        elif status['is_running']:
            self.tray.update_status("Auto-sync enabled")
        else:
            self.tray.update_status("Idle")
        
        # Update menu state
        self.tray.update_menu_state(status['is_running'])
    
    def quit_application(self):
        """Quit the application."""
        self.logger.info("Quitting application...")
        
        # Stop sync engine
        if self.sync_engine.is_running:
            self.sync_engine.stop_auto_sync()
        
        # Quit Qt application
        self.app.quit()
    
    def signal_handler(self, sig, frame):
        """Handle interrupt signal (Ctrl+C)."""
        print("\nInterrupt received, quitting...")
        self.quit_application()


def main():
    """Main entry point."""
    app = ProtonDriveSyncApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
