"""Main GUI window for ProtonDrive Sync."""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QGroupBox, QLineEdit, QFileDialog,
    QComboBox, QSpinBox, QCheckBox, QDialog, QDialogButtonBox,
    QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

from .config_manager import ConfigManager
from .rclone_manager import RcloneManager
from .sync_engine import SyncEngine


class SetupWizard(QDialog):
    """First-run setup wizard."""
    
    def __init__(self, config: ConfigManager, rclone: RcloneManager, parent=None):
        super().__init__(parent)
        self.config = config
        self.rclone = rclone
        self.setWindowTitle("ProtonDrive Sync - Setup Wizard")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Welcome message
        welcome_label = QLabel(
            "<h2>Welcome to ProtonDrive Sync!</h2>"
            "<p>Let's configure your sync settings.</p>"
        )
        welcome_label.setWordWrap(True)
        layout.addWidget(welcome_label)
        
        # Rclone remote selection
        remote_group = QGroupBox("Rclone Remote")
        remote_layout = QVBoxLayout()
        
        remote_layout.addWidget(QLabel("Select your ProtonDrive remote:"))
        self.remote_combo = QComboBox()
        
        # Populate remotes
        remotes = self.rclone.list_remotes()
        if remotes:
            self.remote_combo.addItems(remotes)
        else:
            self.remote_combo.addItem("No remotes found")
        
        remote_layout.addWidget(self.remote_combo)
        
        test_btn = QPushButton("Test Remote")
        test_btn.clicked.connect(self.test_remote)
        remote_layout.addWidget(test_btn)
        
        self.remote_status = QLabel("")
        remote_layout.addWidget(self.remote_status)
        
        remote_group.setLayout(remote_layout)
        layout.addWidget(remote_group)
        
        # Local folder selection
        folder_group = QGroupBox("Local Sync Folder")
        folder_layout = QVBoxLayout()
        
        folder_layout.addWidget(QLabel("Choose where to sync your files:"))
        
        folder_select_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("/home/user/ProtonDrive")
        folder_select_layout.addWidget(self.folder_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)
        folder_select_layout.addWidget(browse_btn)
        
        folder_layout.addLayout(folder_select_layout)
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # Auto sync settings
        auto_group = QGroupBox("Auto Sync Settings")
        auto_layout = QVBoxLayout()
        
        self.auto_sync_check = QCheckBox("Enable automatic sync")
        auto_layout.addWidget(self.auto_sync_check)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Sync interval (minutes):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(5)
        self.interval_spin.setMaximum(1440)
        self.interval_spin.setValue(30)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        auto_layout.addLayout(interval_layout)
        
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Sync Folder",
            str(Path.home())
        )
        if folder:
            self.folder_edit.setText(folder)
    
    def test_remote(self):
        remote = self.remote_combo.currentText()
        if remote == "No remotes found":
            self.remote_status.setText("❌ No remotes configured")
            self.remote_status.setStyleSheet("color: red;")
            return
        
        self.remote_status.setText("⏳ Testing remote...")
        self.remote_status.setStyleSheet("color: blue;")
        QApplication.processEvents()
        
        success, message = self.rclone.test_remote(remote)
        if success:
            self.remote_status.setText(f"✅ {message}")
            self.remote_status.setStyleSheet("color: green;")
        else:
            self.remote_status.setText(f"❌ {message}")
            self.remote_status.setStyleSheet("color: red;")
    
    def validate_and_accept(self):
        remote = self.remote_combo.currentText()
        folder = self.folder_edit.text()
        
        if remote == "No remotes found" or not remote:
            QMessageBox.warning(self, "Invalid Configuration", 
                              "Please select a valid rclone remote.")
            return
        
        if not folder:
            QMessageBox.warning(self, "Invalid Configuration",
                              "Please select a local sync folder.")
            return
        
        # Save configuration
        self.config.update({
            "rclone_remote": remote,
            "local_folder": folder,
            "auto_sync_enabled": self.auto_sync_check.isChecked(),
            "sync_interval_minutes": self.interval_spin.value()
        })
        self.config.mark_setup_complete()
        self.config.save_config()
        
        self.accept()


class MainWindow(QMainWindow):
    """Main application window."""
    
    # Signals
    show_notification = pyqtSignal(str, str)
    
    def __init__(
        self,
        config: ConfigManager,
        rclone: RcloneManager,
        sync_engine: SyncEngine,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__()
        self.config = config
        self.rclone = rclone
        self.sync_engine = sync_engine
        self.logger = logger or logging.getLogger(__name__)
        
        self.setWindowTitle("ProtonDrive Sync")
        self.setMinimumSize(700, 500)
        
        # Setup callbacks
        self.sync_engine.on_sync_start = self.on_sync_start
        self.sync_engine.on_sync_complete = self.on_sync_complete
        self.sync_engine.on_sync_progress = self.on_sync_progress
        
        self.setup_ui()
        self.update_status()
        
        # Start update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Status section
        status_group = QGroupBox("Sync Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout.addWidget(self.status_label)
        
        self.last_sync_label = QLabel("Last sync: Never")
        status_layout.addWidget(self.last_sync_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Configuration section
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()
        
        self.remote_label = QLabel(f"Remote: {self.config.get('rclone_remote', 'Not configured')}")
        config_layout.addWidget(self.remote_label)
        
        self.folder_label = QLabel(f"Local folder: {self.config.get('local_folder', 'Not configured')}")
        config_layout.addWidget(self.folder_label)
        
        self.auto_sync_label = QLabel(
            f"Auto sync: {'Enabled' if self.config.get('auto_sync_enabled') else 'Disabled'}"
        )
        config_layout.addWidget(self.auto_sync_label)
        
        config_buttons = QHBoxLayout()
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        config_buttons.addWidget(self.settings_btn)
        
        config_buttons.addStretch()
        config_layout.addLayout(config_buttons)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.sync_btn = QPushButton("▶️ Sync Now")
        self.sync_btn.clicked.connect(self.manual_sync)
        self.sync_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; }")
        button_layout.addWidget(self.sync_btn)
        
        self.cancel_btn = QPushButton("⏹️ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_sync)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; }")
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Activity log
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_log_btn)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        central_widget.setLayout(layout)
        
        self.log_message("Application started")
    
    def update_status(self):
        """Update status display."""
        status = self.sync_engine.get_status()
        
        if status['sync_in_progress']:
            self.status_label.setText("Status: 🔄 Syncing...")
            self.status_label.setStyleSheet("color: blue;")
        elif status['is_running']:
            self.status_label.setText("Status: ✅ Auto-sync enabled")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Status: ⏸️ Idle")
            self.status_label.setStyleSheet("color: gray;")
        
        if status['last_sync_time']:
            last_sync = datetime.fromisoformat(status['last_sync_time'])
            time_str = last_sync.strftime("%Y-%m-%d %H:%M:%S")
            self.last_sync_label.setText(f"Last sync: {time_str}")
        else:
            self.last_sync_label.setText("Last sync: Never")
        
        # Update button states
        self.sync_btn.setEnabled(not status['sync_in_progress'])
        self.cancel_btn.setEnabled(status['sync_in_progress'])
    
    def manual_sync(self):
        """Trigger manual sync."""
        if not self.config.is_configured():
            QMessageBox.warning(
                self,
                "Not Configured",
                "Please configure the application in Settings first."
            )
            self.show_settings()
            return
        
        self.log_message("Starting manual sync...")
        self.sync_engine.sync_now()
    
    def cancel_sync(self):
        """Cancel ongoing sync."""
        reply = QMessageBox.question(
            self,
            "Cancel Sync",
            "Are you sure you want to cancel the sync?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.sync_engine.cancel_sync():
                self.log_message("Sync cancelled by user")
            else:
                self.log_message("Failed to cancel sync")
    
    def show_settings(self):
        """Show settings/setup dialog."""
        wizard = SetupWizard(self.config, self.rclone, self)
        
        # Pre-fill current values
        remotes = self.rclone.list_remotes()
        current_remote = self.config.get('rclone_remote', '')
        if current_remote in remotes:
            wizard.remote_combo.setCurrentText(current_remote)
        
        wizard.folder_edit.setText(self.config.get('local_folder', ''))
        wizard.auto_sync_check.setChecked(self.config.get('auto_sync_enabled', False))
        wizard.interval_spin.setValue(self.config.get('sync_interval_minutes', 30))
        
        if wizard.exec_() == QDialog.Accepted:
            # Update UI with new config
            self.remote_label.setText(f"Remote: {self.config.get('rclone_remote')}")
            self.folder_label.setText(f"Local folder: {self.config.get('local_folder')}")
            self.auto_sync_label.setText(
                f"Auto sync: {'Enabled' if self.config.get('auto_sync_enabled') else 'Disabled'}"
            )
            self.log_message("Configuration updated")
            
            # Restart auto-sync if enabled
            if self.config.get('auto_sync_enabled'):
                self.sync_engine.stop_auto_sync()
                self.sync_engine.start_auto_sync()
                self.log_message("Auto-sync restarted")
    
    def log_message(self, message: str):
        """Add message to activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def clear_log(self):
        """Clear activity log."""
        self.log_text.clear()
    
    def on_sync_start(self):
        """Callback when sync starts."""
        self.log_message("Sync started")
        self.show_notification.emit("ProtonDrive Sync", "Sync started")
    
    def on_sync_complete(self, success: bool, message: str):
        """Callback when sync completes."""
        if success:
            self.log_message("✅ Sync completed successfully")
            self.show_notification.emit("ProtonDrive Sync", "Sync completed successfully")
        else:
            self.log_message(f"❌ Sync failed: {message}")
            self.show_notification.emit("ProtonDrive Sync", f"Sync failed: {message}")
    
    def on_sync_progress(self, line: str):
        """Callback for sync progress updates."""
        # Only log important progress lines to avoid spam
        if "Transferred:" in line or "Errors:" in line or "Checks:" in line:
            self.log_message(line)
    
    def closeEvent(self, event):
        """Handle window close event."""
        event.ignore()
        self.hide()
