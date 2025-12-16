"""Enhanced GUI with ProtonDrive authentication and selective sync."""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QGroupBox, QLineEdit, QFileDialog,
    QComboBox, QSpinBox, QCheckBox, QDialog, QDialogButtonBox,
    QMessageBox, QApplication, QWizard, QWizardPage, QTreeWidget,
    QTreeWidgetItem, QProgressBar, QRadioButton, QButtonGroup,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import logging
import subprocess
import webbrowser

from .config_manager import ConfigManager
from .rclone_manager import RcloneManager
from .sync_engine import SyncEngine
from .protondrive_wizard import ModernProtonDriveAuthWizard


class ProtonDriveAuthPage(QWizardPage):
    """ProtonDrive authentication wizard page."""
    
    def __init__(self, rclone: RcloneManager, parent=None):
        super().__init__(parent)
        self.rclone = rclone
        self.setTitle("🔐 ProtonDrive Authentication")
        self.setSubTitle("Let's connect your ProtonDrive account")
        
        layout = QVBoxLayout()
        
        # Welcome message
        welcome = QLabel(
            "<h3>Welcome to ProtonDrive Sync!</h3>"
            "<p>First, we need to connect to your ProtonDrive account.</p>"
        )
        welcome.setWordWrap(True)
        layout.addWidget(welcome)
        
        # Check if ProtonDrive is configured
        has_pd, pd_remote = self.rclone.has_protondrive_remote()
        
        if has_pd:
            # ProtonDrive already configured
            success_label = QLabel(
                f"<p style='color: green;'>✅ <b>Great news!</b> We found a ProtonDrive remote: <b>{pd_remote}</b></p>"
                "<p>You can proceed to the next step.</p>"
            )
            success_label.setWordWrap(True)
            layout.addWidget(success_label)
            
            self.remote_name = pd_remote
            self.setField("protondrive_remote", pd_remote)
        else:
            # Need to configure ProtonDrive
            warning_label = QLabel(
                "<p style='color: orange;'>⚠️ <b>ProtonDrive not configured yet</b></p>"
                "<p>We'll help you set it up in just a few steps.</p>"
            )
            warning_label.setWordWrap(True)
            layout.addWidget(warning_label)
            
            # Instructions
            instructions = QGroupBox("📖 What you'll need:")
            inst_layout = QVBoxLayout()
            
            inst_text = QLabel(
                "<ol>"
                "<li><b>ProtonDrive account</b> (free or paid)</li>"
                "<li><b>ProtonDrive password</b></li>"
                "<li><b>2FA code</b> (if you have 2FA enabled)</li>"
                "</ol>"
                "<p><i>We'll guide you through the rclone configuration process.</i></p>"
            )
            inst_text.setWordWrap(True)
            inst_layout.addWidget(inst_text)
            instructions.setLayout(inst_layout)
            layout.addWidget(instructions)
            
            # Setup button
            setup_btn = QPushButton("🔧 Configure ProtonDrive Now")
            setup_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; background-color: #6d4aff; color: white; }")
            setup_btn.clicked.connect(self.launch_rclone_config)
            layout.addWidget(setup_btn)
            
            # Help button
            help_btn = QPushButton("📚 Open ProtonDrive rclone Documentation")
            help_btn.clicked.connect(lambda: webbrowser.open("https://rclone.org/protondrive/"))
            layout.addWidget(help_btn)
            
            # Refresh button
            refresh_btn = QPushButton("🔄 Refresh - I've configured rclone")
            refresh_btn.clicked.connect(self.refresh_check)
            layout.addWidget(refresh_btn)
            
            self.status_label = QLabel("")
            layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Register field
        self.registerField("protondrive_remote*", QLineEdit())
    
    def launch_rclone_config(self):
        """Launch modern ProtonDrive configuration wizard."""
        wizard = ModernProtonDriveAuthWizard(self.rclone, self)
        
        if wizard.exec_() == QDialog.Accepted:
            # Configuration successful, refresh the page
            self.refresh_check()
        else:
            # User cancelled
            self.status_label.setText(
                "<p style='color: orange;'>⚠️ Configuration cancelled. Click 'Configure ProtonDrive Now' to try again.</p>"
            )
    
    def refresh_check(self):
        """Refresh to check if ProtonDrive is now configured."""
        has_pd, pd_remote = self.rclone.has_protondrive_remote()
        
        if has_pd:
            self.status_label.setText(f"<p style='color: green;'>✅ ProtonDrive found: <b>{pd_remote}</b></p>")
            self.status_label.setStyleSheet("color: green;")
            self.remote_name = pd_remote
            self.setField("protondrive_remote", pd_remote)
            QMessageBox.information(
                self,
                "Success!",
                f"<h3>🎉 ProtonDrive configured successfully!</h3>"
                f"<p>Remote name: <b>{pd_remote}</b></p>"
                "<p>Click 'Next' to continue with setup.</p>"
            )
        else:
            self.status_label.setText("<p style='color: red;'>❌ ProtonDrive not found. Please configure rclone first.</p>")
            self.status_label.setStyleSheet("color: red;")
    
    def validatePage(self):
        """Validate that ProtonDrive is configured."""
        has_pd, pd_remote = self.rclone.has_protondrive_remote()
        if not has_pd:
            QMessageBox.warning(
                self,
                "ProtonDrive Not Configured",
                "<p>Please configure ProtonDrive with rclone before continuing.</p>"
                "<p>Click the <b>'Configure ProtonDrive Now'</b> button and follow the instructions.</p>"
            )
            return False
        
        # Test the remote
        self.setField("protondrive_remote", pd_remote)
        success, message = self.rclone.test_remote(pd_remote)
        if not success:
            QMessageBox.warning(
                self,
                "Connection Test Failed",
                f"<p>Could not connect to ProtonDrive remote '{pd_remote}'.</p>"
                f"<p><b>Error:</b> {message}</p>"
                "<p>Please check your configuration and try again.</p>"
            )
            return False
        
        return True


class SelectiveSyncPage(QWizardPage):
    """Selective sync wizard page."""
    
    def __init__(self, config: ConfigManager, rclone: RcloneManager, parent=None):
        super().__init__(parent)
        self.config = config
        self.rclone = rclone
        self.setTitle("📁 Select Folders to Sync")
        self.setSubTitle("Choose which folders to sync from your ProtonDrive")
        
        layout = QVBoxLayout()
        
        # Sync mode selection
        mode_group = QGroupBox("Sync Mode")
        mode_layout = QVBoxLayout()
        
        self.mode_group = QButtonGroup()
        
        self.full_radio = QRadioButton("🔄 Sync entire ProtonDrive (recommended for most users)")
        self.full_radio.setChecked(True)
        self.full_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.full_radio, 0)
        mode_layout.addWidget(self.full_radio)
        
        self.selective_radio = QRadioButton("✅ Select specific folders to sync")
        self.selective_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.selective_radio, 1)
        mode_layout.addWidget(self.selective_radio)
        
        self.exclude_radio = QRadioButton("❌ Exclude specific folders from sync")
        self.exclude_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.exclude_radio, 2)
        mode_layout.addWidget(self.exclude_radio)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Folder tree
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("ProtonDrive Folders")
        self.tree_widget.setEnabled(False)
        layout.addWidget(self.tree_widget)
        
        # Load folders button
        self.load_btn = QPushButton("📂 Load Folder Structure")
        self.load_btn.clicked.connect(self.load_folders)
        self.load_btn.setEnabled(False)
        layout.addWidget(self.load_btn)
        
        # Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        # Warning
        warning = QLabel(
            "<p style='color: #666; font-size: 11px;'>"
            "💡 <b>Tip:</b> If you're not sure what to sync, choose 'Sync entire ProtonDrive'. "
            "You can always change this later in settings."
            "</p>"
        )
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        self.setLayout(layout)
    
    def on_mode_changed(self):
        """Handle sync mode change."""
        if self.full_radio.isChecked():
            self.tree_widget.setEnabled(False)
            self.load_btn.setEnabled(False)
        else:
            self.tree_widget.setEnabled(True)
            self.load_btn.setEnabled(True)
    
    def load_folders(self):
        """Load folder structure from ProtonDrive."""
        remote = self.field("protondrive_remote")
        if not remote:
            return
        
        self.status_label.setText("⏳ Loading folders...")
        QApplication.processEvents()
        
        try:
            folders = self.rclone.list_folders(remote)
            self.tree_widget.clear()
            
            for folder in folders:
                item = QTreeWidgetItem([folder["name"]])
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Unchecked)
                item.setData(0, Qt.UserRole, folder["path"])
                self.tree_widget.addTopLevelItem(item)
                
                # Try to load subfolder (one level)
                subfolders = self.rclone.list_folders(remote, folder["path"])
                for subfolder in subfolders:
                    subitem = QTreeWidgetItem([subfolder["name"]])
                    subitem.setFlags(subitem.flags() | Qt.ItemIsUserCheckable)
                    subitem.setCheckState(0, Qt.Unchecked)
                    subitem.setData(0, Qt.UserRole, subfolder["path"])
                    item.addChild(subitem)
            
            self.status_label.setText(f"✅ Loaded {len(folders)} folders")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error loading folders: {str(e)}")
    
    def validatePage(self):
        """Validate and save sync preferences."""
        if self.full_radio.isChecked():
            self.config.set("sync_mode", "full")
            self.config.set("included_folders", [])
            self.config.set("excluded_folders", [])
        elif self.selective_radio.isChecked():
            # Get checked folders
            included = []
            for i in range(self.tree_widget.topLevelItemCount()):
                item = self.tree_widget.topLevelItem(i)
                if item.checkState(0) == Qt.Checked:
                    included.append(item.data(0, Qt.UserRole))
                # Check children
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.checkState(0) == Qt.Checked:
                        included.append(child.data(0, Qt.UserRole))
            
            if not included:
                QMessageBox.warning(
                    self,
                    "No Folders Selected",
                    "<p>Please select at least one folder to sync.</p>"
                    "<p>Or choose 'Sync entire ProtonDrive' instead.</p>"
                )
                return False
            
            self.config.set("sync_mode", "selective_include")
            self.config.set("included_folders", included)
            self.config.set("excluded_folders", [])
        else:  # exclude mode
            # Get checked folders
            excluded = []
            for i in range(self.tree_widget.topLevelItemCount()):
                item = self.tree_widget.topLevelItem(i)
                if item.checkState(0) == Qt.Checked:
                    excluded.append(item.data(0, Qt.UserRole))
                # Check children
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.checkState(0) == Qt.Checked:
                        excluded.append(child.data(0, Qt.UserRole))
            
            self.config.set("sync_mode", "selective_exclude")
            self.config.set("included_folders", [])
            self.config.set("excluded_folders", excluded)
        
        return True


class LocalFolderPage(QWizardPage):
    """Local folder selection page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("💾 Choose Local Folder")
        self.setSubTitle("Select where to store your synced files")
        
        layout = QVBoxLayout()
        
        # Info
        info = QLabel(
            "<p>Choose a folder on your computer where ProtonDrive files will be synced.</p>"
            "<p style='color: #666;'>"
            "💡 <b>Tip:</b> Make sure you have enough free space. "
            "We recommend ~/ProtonDrive or ~/Documents/ProtonDrive"
            "</p>"
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText(str(Path.home() / "ProtonDrive"))
        self.folder_edit.setText(str(Path.home() / "ProtonDrive"))
        folder_layout.addWidget(self.folder_edit)
        
        browse_btn = QPushButton("📂 Browse...")
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_btn)
        
        layout.addLayout(folder_layout)
        
        # Register field
        self.registerField("local_folder*", self.folder_edit)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def browse_folder(self):
        """Browse for folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Sync Folder",
            str(Path.home())
        )
        if folder:
            self.folder_edit.setText(folder)


class SyncSettingsPage(QWizardPage):
    """Sync settings configuration page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("⚙️ Sync Settings")
        self.setSubTitle("Configure automatic sync and other preferences")
        
        layout = QVBoxLayout()
        
        # Auto sync
        auto_group = QGroupBox("Automatic Sync")
        auto_layout = QVBoxLayout()
        
        self.auto_sync_check = QCheckBox("✅ Enable automatic background sync (recommended)")
        self.auto_sync_check.setChecked(True)
        auto_layout.addWidget(self.auto_sync_check)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Check for changes every:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(5)
        self.interval_spin.setMaximum(1440)
        self.interval_spin.setValue(30)
        self.interval_spin.setSuffix(" minutes")
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        auto_layout.addLayout(interval_layout)
        
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # Safety settings
        safety_group = QGroupBox("Safety Features")
        safety_layout = QVBoxLayout()
        
        self.dry_run_check = QCheckBox("🔍 Perform dry-run before first sync (recommended)")
        self.dry_run_check.setChecked(True)
        safety_layout.addWidget(self.dry_run_check)
        
        self.confirm_large_check = QCheckBox("⚠️ Warn before syncing large amounts of data")
        self.confirm_large_check.setChecked(True)
        safety_layout.addWidget(self.confirm_large_check)
        
        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)
        
        # Bandwidth limit
        bw_group = QGroupBox("Bandwidth Limit (Optional)")
        bw_layout = QVBoxLayout()
        
        bw_info = QLabel(
            "<p style='color: #666; font-size: 11px;'>"
            "Limit download/upload speed to prevent network saturation. "
            "Leave at 0 for unlimited."
            "</p>"
        )
        bw_info.setWordWrap(True)
        bw_layout.addWidget(bw_info)
        
        bw_input_layout = QHBoxLayout()
        bw_input_layout.addWidget(QLabel("Bandwidth limit:"))
        self.bw_spin = QSpinBox()
        self.bw_spin.setMinimum(0)
        self.bw_spin.setMaximum(100000)
        self.bw_spin.setValue(0)
        self.bw_spin.setSuffix(" KB/s")
        self.bw_spin.setSpecialValueText("Unlimited")
        bw_input_layout.addWidget(self.bw_spin)
        bw_input_layout.addStretch()
        bw_layout.addLayout(bw_input_layout)
        
        bw_group.setLayout(bw_layout)
        layout.addWidget(bw_group)
        
        # Register fields
        self.registerField("auto_sync", self.auto_sync_check)
        self.registerField("sync_interval", self.interval_spin)
        self.registerField("dry_run_first", self.dry_run_check)
        self.registerField("confirm_large", self.confirm_large_check)
        self.registerField("bandwidth_limit", self.bw_spin)
        
        layout.addStretch()
        self.setLayout(layout)


class ReviewPage(QWizardPage):
    """Review and confirm settings page."""
    
    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config
        self.setTitle("✅ Review Your Settings")
        self.setSubTitle("Please review your configuration before completing setup")
        
        self.layout = QVBoxLayout()
        
        # Create scroll area for review
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.review_layout = QVBoxLayout()
        scroll_widget.setLayout(self.review_layout)
        scroll.setWidget(scroll_widget)
        
        self.layout.addWidget(scroll)
        self.setLayout(self.layout)
    
    def initializePage(self):
        """Initialize the review page with current settings."""
        # Clear previous content
        while self.review_layout.count():
            item = self.review_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get all settings
        remote = self.field("protondrive_remote")
        local_folder = self.field("local_folder")
        auto_sync = self.field("auto_sync")
        interval = self.field("sync_interval")
        dry_run = self.field("dry_run_first")
        confirm_large = self.field("confirm_large")
        bandwidth = self.field("bandwidth_limit")
        
        sync_mode = self.config.get("sync_mode", "full")
        included = self.config.get("included_folders", [])
        excluded = self.config.get("excluded_folders", [])
        
        # Display settings
        settings_text = f"""
        <h3>📋 Configuration Summary</h3>
        
        <h4>🔐 ProtonDrive Connection</h4>
        <ul>
        <li><b>Remote:</b> {remote}</li>
        </ul>
        
        <h4>📁 Sync Configuration</h4>
        <ul>
        <li><b>Local folder:</b> {local_folder}</li>
        <li><b>Sync mode:</b> {sync_mode.replace('_', ' ').title()}</li>
        """
        
        if sync_mode == "selective_include" and included:
            settings_text += f"<li><b>Included folders:</b> {', '.join(included)}</li>"
        elif sync_mode == "selective_exclude" and excluded:
            settings_text += f"<li><b>Excluded folders:</b> {', '.join(excluded)}</li>"
        
        settings_text += f"""
        </ul>
        
        <h4>⚙️ Sync Settings</h4>
        <ul>
        <li><b>Auto sync:</b> {'Enabled' if auto_sync else 'Disabled'}</li>
        <li><b>Sync interval:</b> {interval} minutes</li>
        <li><b>Dry-run first sync:</b> {'Yes' if dry_run else 'No'}</li>
        <li><b>Warn before large sync:</b> {'Yes' if confirm_large else 'No'}</li>
        <li><b>Bandwidth limit:</b> {bandwidth if bandwidth > 0 else 'Unlimited'} KB/s</li>
        </ul>
        
        <p style='color: green;'><b>✅ Everything looks good! Click 'Finish' to start syncing.</b></p>
        """
        
        label = QLabel(settings_text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        self.review_layout.addWidget(label)
        
        self.review_layout.addStretch()


class EnhancedSetupWizard(QWizard):
    """Enhanced multi-step setup wizard."""
    
    def __init__(self, config: ConfigManager, rclone: RcloneManager, parent=None):
        super().__init__(parent)
        self.config = config
        self.rclone = rclone
        
        self.setWindowTitle("ProtonDrive Sync - Setup Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.HaveHelpButton, False)
        self.setOption(QWizard.NoBackButtonOnStartPage, False)
        self.setMinimumSize(800, 600)
        
        # Add pages
        self.auth_page = ProtonDriveAuthPage(rclone, self)
        self.addPage(self.auth_page)
        
        self.sync_page = SelectiveSyncPage(config, rclone, self)
        self.addPage(self.sync_page)
        
        self.folder_page = LocalFolderPage(self)
        self.addPage(self.folder_page)
        
        self.settings_page = SyncSettingsPage(self)
        self.addPage(self.settings_page)
        
        self.review_page = ReviewPage(config, self)
        self.addPage(self.review_page)
    
    def accept(self):
        """Save configuration and complete setup."""
        # Save all settings
        self.config.update({
            "rclone_remote": self.field("protondrive_remote"),
            "local_folder": self.field("local_folder"),
            "auto_sync_enabled": self.field("auto_sync"),
            "sync_interval_minutes": self.field("sync_interval"),
            "dry_run_first_sync": self.field("dry_run_first"),
            "confirm_large_sync": self.field("confirm_large"),
            "bandwidth_limit_kbps": self.field("bandwidth_limit"),
            "protondrive_configured": True,
            "protondrive_remote_tested": True,
            "setup_completed": True
        })
        self.config.mark_setup_complete()
        self.config.save_config()
        
        super().accept()


class MainWindow(QMainWindow):
    """Main application window with enhanced features."""
    
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
        self.setMinimumSize(700, 600)
        
        # Setup callbacks
        self.sync_engine.on_sync_start = self.on_sync_start
        self.sync_engine.on_sync_complete = self.on_sync_complete
        self.sync_engine.on_sync_progress = self.on_sync_progress
        self.sync_engine.on_sync_warning = self.on_sync_warning
        
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
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Configuration section
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()
        
        self.remote_label = QLabel(f"Remote: {self.config.get('rclone_remote', 'Not configured')}")
        config_layout.addWidget(self.remote_label)
        
        self.folder_label = QLabel(f"Local folder: {self.config.get('local_folder', 'Not configured')}")
        config_layout.addWidget(self.folder_label)
        
        sync_mode = self.config.get("sync_mode", "full")
        self.sync_mode_label = QLabel(f"Sync mode: {sync_mode.replace('_', ' ').title()}")
        config_layout.addWidget(self.sync_mode_label)
        
        self.auto_sync_label = QLabel(
            f"Auto sync: {'Enabled' if self.config.get('auto_sync_enabled') else 'Disabled'}"
        )
        config_layout.addWidget(self.auto_sync_label)
        
        config_buttons = QHBoxLayout()
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        config_buttons.addWidget(self.settings_btn)
        
        self.manage_folders_btn = QPushButton("📁 Manage Synced Folders")
        self.manage_folders_btn.clicked.connect(self.manage_folders)
        config_buttons.addWidget(self.manage_folders_btn)
        
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
        
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.clicked.connect(self.pause_sync)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; }")
        button_layout.addWidget(self.pause_btn)
        
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
            if status.get('sync_paused'):
                self.status_label.setText("Status: ⏸️ Paused")
                self.status_label.setStyleSheet("color: orange;")
            else:
                self.status_label.setText("Status: 🔄 Syncing...")
                self.status_label.setStyleSheet("color: blue;")
                self.progress_bar.setVisible(True)
        elif status['is_running']:
            self.status_label.setText("Status: ✅ Auto-sync enabled")
            self.status_label.setStyleSheet("color: green;")
            self.progress_bar.setVisible(False)
        else:
            self.status_label.setText("Status: ⏸️ Idle")
            self.status_label.setStyleSheet("color: gray;")
            self.progress_bar.setVisible(False)
        
        if status['last_sync_time']:
            last_sync = datetime.fromisoformat(status['last_sync_time'])
            time_str = last_sync.strftime("%Y-%m-%d %H:%M:%S")
            self.last_sync_label.setText(f"Last sync: {time_str}")
        else:
            self.last_sync_label.setText("Last sync: Never")
        
        # Update button states
        self.sync_btn.setEnabled(not status['sync_in_progress'])
        self.cancel_btn.setEnabled(status['sync_in_progress'])
        self.pause_btn.setEnabled(status['sync_in_progress'] and not status.get('sync_paused'))
    
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
    
    def pause_sync(self):
        """Pause ongoing sync."""
        if self.sync_engine.pause_sync():
            self.log_message("Sync paused")
            self.pause_btn.setText("▶️ Resume")
            self.pause_btn.clicked.disconnect()
            self.pause_btn.clicked.connect(self.resume_sync)
    
    def resume_sync(self):
        """Resume paused sync."""
        if self.sync_engine.resume_sync():
            self.log_message("Sync resumed")
            self.pause_btn.setText("⏸️ Pause")
            self.pause_btn.clicked.disconnect()
            self.pause_btn.clicked.connect(self.pause_sync)
    
    def show_settings(self):
        """Show settings/setup dialog."""
        wizard = EnhancedSetupWizard(self.config, self.rclone, self)
        
        if wizard.exec_() == QDialog.Accepted:
            # Update UI with new config
            self.remote_label.setText(f"Remote: {self.config.get('rclone_remote')}")
            self.folder_label.setText(f"Local folder: {self.config.get('local_folder')}")
            sync_mode = self.config.get("sync_mode", "full")
            self.sync_mode_label.setText(f"Sync mode: {sync_mode.replace('_', ' ').title()}")
            self.auto_sync_label.setText(
                f"Auto sync: {'Enabled' if self.config.get('auto_sync_enabled') else 'Disabled'}"
            )
            self.log_message("Configuration updated")
            
            # Restart auto-sync if enabled
            if self.config.get('auto_sync_enabled'):
                self.sync_engine.stop_auto_sync()
                self.sync_engine.start_auto_sync()
                self.log_message("Auto-sync restarted")
    
    def manage_folders(self):
        """Manage synced folders."""
        # Open the selective sync page
        wizard = EnhancedSetupWizard(self.config, self.rclone, self)
        wizard.setStartId(1)  # Start at selective sync page
        wizard.exec_()
    
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
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
    
    def on_sync_complete(self, success: bool, message: str):
        """Callback when sync completes."""
        if success:
            self.log_message("✅ Sync completed successfully")
            self.show_notification.emit("ProtonDrive Sync", "Sync completed successfully")
        else:
            self.log_message(f"❌ Sync failed: {message}")
            self.show_notification.emit("ProtonDrive Sync", f"Sync failed: {message}")
        
        self.progress_bar.setVisible(False)
    
    def on_sync_progress(self, line: str):
        """Callback for sync progress updates."""
        # Only log important progress lines to avoid spam
        if "Transferred:" in line or "Errors:" in line or "Checks:" in line:
            self.log_message(line)
    
    def on_sync_warning(self, warning_type: str, data: dict):
        """Callback for sync warnings."""
        if warning_type == "large_sync":
            size_gb = data.get("size_gb", 0)
            size_mb = data.get("size_mb", 0)
            count = data.get("count", 0)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Large Sync Detected")
            msg.setText(f"<h3>⚠️ Large sync detected</h3>")
            msg.setInformativeText(
                f"<p>This sync will transfer:</p>"
                f"<ul>"
                f"<li><b>{size_gb:.2f} GB</b> ({size_mb:.2f} MB)</li>"
                f"<li><b>{count}</b> files</li>"
                f"</ul>"
                f"<p>This may take a while and use significant bandwidth.</p>"
                f"<p>Do you want to continue?</p>"
            )
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            
            reply = msg.exec_()
            if reply != QMessageBox.Yes:
                self.sync_engine.cancel_sync()
                self.log_message("Sync cancelled by user due to large size")
    
    def closeEvent(self, event):
        """Handle window close event."""
        event.ignore()
        self.hide()
