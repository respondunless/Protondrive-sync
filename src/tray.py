"""System tray implementation for ProtonDrive Sync."""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, qApp
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from typing import Optional

from .sync_engine import SyncEngine
from .config_manager import ConfigManager


class SystemTray(QObject):
    """System tray icon and menu."""
    
    # Signals
    show_window = pyqtSignal()
    quit_app = pyqtSignal()
    
    def __init__(
        self,
        config: ConfigManager,
        sync_engine: SyncEngine,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__()
        self.config = config
        self.sync_engine = sync_engine
        self.logger = logger or logging.getLogger(__name__)
        
        self.tray_icon = None
        self.setup_tray()
    
    def setup_tray(self):
        """Setup system tray icon and menu."""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set icon (use default icon if custom not available)
        # You can replace this with a custom icon file
        icon = qApp.style().standardIcon(qApp.style().SP_DriveNetIcon)
        self.tray_icon.setIcon(icon)
        
        # Create menu
        menu = QMenu()
        
        # Open window action
        open_action = QAction("📂 Open ProtonDrive Sync", self)
        open_action.triggered.connect(self.show_window.emit)
        menu.addAction(open_action)
        
        menu.addSeparator()
        
        # Start sync action
        self.start_sync_action = QAction("▶️ Start Auto-Sync", self)
        self.start_sync_action.triggered.connect(self.start_auto_sync)
        menu.addAction(self.start_sync_action)
        
        # Stop sync action
        self.stop_sync_action = QAction("⏹️ Stop Auto-Sync", self)
        self.stop_sync_action.triggered.connect(self.stop_auto_sync)
        self.stop_sync_action.setEnabled(False)
        menu.addAction(self.stop_sync_action)
        
        # Sync now action
        sync_now_action = QAction("🔄 Sync Now", self)
        sync_now_action.triggered.connect(self.sync_now)
        menu.addAction(sync_now_action)
        
        menu.addSeparator()
        
        # Status action (disabled, just shows status)
        self.status_action = QAction("Status: Idle", self)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        menu.addSeparator()
        
        # Quit action
        quit_action = QAction("❌ Quit", self)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)
        
        # Set menu to tray icon
        self.tray_icon.setContextMenu(menu)
        
        # Connect double-click to show window
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Set tooltip
        self.tray_icon.setToolTip("ProtonDrive Sync")
        
        # Show tray icon
        self.tray_icon.show()
        
        self.logger.info("System tray initialized")
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window.emit()
    
    def start_auto_sync(self):
        """Start automatic sync."""
        if self.sync_engine.start_auto_sync():
            self.start_sync_action.setEnabled(False)
            self.stop_sync_action.setEnabled(True)
            self.status_action.setText("Status: Auto-sync enabled")
            self.show_message("Auto-sync started", "Automatic sync is now enabled")
            self.logger.info("Auto-sync started from tray")
        else:
            self.show_message(
                "Cannot start auto-sync",
                "Please configure the application first.",
                QSystemTrayIcon.Warning
            )
    
    def stop_auto_sync(self):
        """Stop automatic sync."""
        self.sync_engine.stop_auto_sync()
        self.start_sync_action.setEnabled(True)
        self.stop_sync_action.setEnabled(False)
        self.status_action.setText("Status: Idle")
        self.show_message("Auto-sync stopped", "Automatic sync is now disabled")
        self.logger.info("Auto-sync stopped from tray")
    
    def sync_now(self):
        """Trigger immediate sync."""
        if self.sync_engine.sync_now():
            self.show_message("Sync started", "Manual sync initiated")
            self.logger.info("Manual sync triggered from tray")
        else:
            self.show_message(
                "Cannot start sync",
                "Sync already in progress or not configured.",
                QSystemTrayIcon.Warning
            )
    
    def quit_application(self):
        """Quit the application."""
        self.logger.info("Quit requested from tray")
        self.quit_app.emit()
    
    def show_message(
        self,
        title: str,
        message: str,
        icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.Information
    ):
        """Show notification message.
        
        Args:
            title: Notification title
            message: Notification message
            icon: Icon type
        """
        if self.tray_icon and self.config.get("notifications_enabled", True):
            self.tray_icon.showMessage(title, message, icon, 5000)
    
    def update_status(self, status: str):
        """Update status in menu.
        
        Args:
            status: Status text
        """
        self.status_action.setText(f"Status: {status}")
    
    def update_menu_state(self, is_auto_sync_running: bool):
        """Update menu item states based on sync status.
        
        Args:
            is_auto_sync_running: Whether auto-sync is running
        """
        self.start_sync_action.setEnabled(not is_auto_sync_running)
        self.stop_sync_action.setEnabled(is_auto_sync_running)
