"""Modern ProtonDrive Authentication Wizard.

This module provides a sleek, user-friendly GUI for authenticating with ProtonDrive,
replacing the command-line rclone config interface.
"""

import subprocess
import re
from typing import Optional, Tuple
from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QProgressBar, QTextEdit,
    QWidget, QFrame, QSpacerItem, QSizePolicy, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor
import logging


class RcloneConfigThread(QThread):
    """Background thread for rclone configuration."""
    
    progress_update = pyqtSignal(str)
    config_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, username: str, password: str, twofa_code: str, 
                 otp_secret: str, remote_name: str, logger: Optional[logging.Logger] = None):
        super().__init__()
        self.username = username
        self.password = password
        self.twofa_code = twofa_code
        self.otp_secret = otp_secret
        self.remote_name = remote_name
        self.logger = logger or logging.getLogger(__name__)
    
    def run(self):
        """Run rclone configuration in background."""
        try:
            self.progress_update.emit("Starting ProtonDrive configuration...")
            
            # Create rclone config programmatically
            # We'll use rclone config create command which is non-interactive
            cmd = [
                "rclone", "config", "create",
                self.remote_name,
                "protondrive",
                "username", self.username,
                "password", self.password
            ]
            
            # Add 2FA if provided
            if self.twofa_code:
                cmd.extend(["2fa", self.twofa_code])
            
            # Add OTP secret if provided
            if self.otp_secret:
                cmd.extend(["otp_secret_key", self.otp_secret])
            
            self.logger.info(f"Configuring rclone with remote name: {self.remote_name}")
            self.progress_update.emit("Authenticating with ProtonDrive...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.progress_update.emit("✅ Configuration successful!")
                self.config_complete.emit(True, "ProtonDrive configured successfully")
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.logger.error(f"Rclone config failed: {error_msg}")
                
                # Try to provide helpful error messages
                if "username" in error_msg.lower() or "password" in error_msg.lower():
                    error_msg = "Invalid username or password. Please check your credentials."
                elif "2fa" in error_msg.lower() or "two" in error_msg.lower():
                    error_msg = "2FA code invalid or expired. Please try again with a fresh code."
                elif "already exists" in error_msg.lower():
                    error_msg = f"A remote named '{self.remote_name}' already exists. Please choose a different name or delete the existing remote."
                
                self.progress_update.emit(f"❌ Configuration failed")
                self.config_complete.emit(False, error_msg)
                
        except subprocess.TimeoutExpired:
            self.progress_update.emit("❌ Configuration timed out")
            self.config_complete.emit(False, "Configuration timed out. Please check your internet connection.")
        except Exception as e:
            self.logger.error(f"Error during configuration: {e}")
            self.progress_update.emit(f"❌ Error: {str(e)}")
            self.config_complete.emit(False, f"Error: {str(e)}")


class ModernProtonDriveAuthWizard(QDialog):
    """Modern, single-page ProtonDrive authentication dialog."""
    
    def __init__(self, rclone_manager, parent=None):
        super().__init__(parent)
        self.rclone = rclone_manager
        self.logger = logging.getLogger(__name__)
        self.config_thread = None
        
        self.setWindowTitle("ProtonDrive Setup")
        self.setMinimumSize(600, 700)
        self.setModal(True)
        
        self.setup_ui()
        self.apply_modern_styling()
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        
        title_label = QLabel("🔐 Connect to ProtonDrive")
        title_label.setObjectName("titleLabel")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Enter your ProtonDrive credentials to get started")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Check if already configured
        has_pd, pd_remote = self.rclone.has_protondrive_remote()
        if has_pd:
            warning_label = QLabel(
                f"<p style='color: #27ae60; padding: 15px; background-color: #d5f4e6; border-radius: 8px;'>"
                f"✅ <b>ProtonDrive already configured</b><br>"
                f"Remote name: <b>{pd_remote}</b><br><br>"
                f"You can proceed with this configuration or click 'Cancel' to use the existing one."
                f"</p>"
            )
            warning_label.setWordWrap(True)
            layout.addWidget(warning_label)
        
        # Remote Name
        remote_frame = self._create_input_field(
            "Remote Name",
            "protondrive",
            "Choose a name for this connection",
            False
        )
        self.remote_name_input = remote_frame.findChild(QLineEdit)
        layout.addWidget(remote_frame)
        
        # Username/Email
        username_frame = self._create_input_field(
            "ProtonDrive Email",
            "your.email@proton.me",
            "Your ProtonDrive account email",
            False
        )
        self.username_input = username_frame.findChild(QLineEdit)
        layout.addWidget(username_frame)
        
        # Password
        password_frame = self._create_input_field(
            "Password",
            "Enter your password",
            "Your ProtonDrive password",
            True
        )
        self.password_input = password_frame.findChild(QLineEdit)
        self.show_password_checkbox = password_frame.findChild(QCheckBox)
        layout.addWidget(password_frame)
        
        # 2FA Section
        twofa_frame = QFrame()
        twofa_frame.setObjectName("sectionFrame")
        twofa_layout = QVBoxLayout()
        
        twofa_header = QLabel("🔑 Two-Factor Authentication (if enabled)")
        twofa_header.setObjectName("sectionHeader")
        twofa_layout.addWidget(twofa_header)
        
        twofa_help = QLabel(
            "If you have 2FA enabled on your ProtonDrive account, enter the 6-digit code from your authenticator app."
        )
        twofa_help.setObjectName("helpText")
        twofa_help.setWordWrap(True)
        twofa_layout.addWidget(twofa_help)
        
        self.twofa_input = QLineEdit()
        self.twofa_input.setPlaceholderText("123456 (optional)")
        self.twofa_input.setMaxLength(6)
        self.twofa_input.setObjectName("modernInput")
        twofa_layout.addWidget(self.twofa_input)
        
        twofa_frame.setLayout(twofa_layout)
        layout.addWidget(twofa_frame)
        
        # OTP Secret Key Section (Advanced)
        otp_frame = QFrame()
        otp_frame.setObjectName("sectionFrame")
        otp_layout = QVBoxLayout()
        
        otp_header = QLabel("🔐 OTP Secret Key (Advanced - Optional)")
        otp_header.setObjectName("sectionHeader")
        otp_layout.addWidget(otp_header)
        
        otp_help = QLabel(
            "Optional: If your ProtonDrive account requires an OTP secret key for two-factor authentication, "
            "you can provide it here. This is typically a long string starting with 'ABCDEFGH...'.\n"
            "Leave blank if you're not sure."
        )
        otp_help.setObjectName("helpText")
        otp_help.setWordWrap(True)
        otp_layout.addWidget(otp_help)
        
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("ABCDEFGHIJKLMNOP... (optional)")
        self.otp_input.setObjectName("modernInput")
        otp_layout.addWidget(self.otp_input)
        
        otp_frame.setLayout(otp_layout)
        layout.addWidget(otp_frame)
        
        # Progress section (initially hidden)
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("progressFrame")
        self.progress_frame.setVisible(False)
        progress_layout = QVBoxLayout()
        
        self.progress_label = QLabel("Configuring ProtonDrive...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMaximumHeight(100)
        progress_layout.addWidget(self.progress_text)
        
        self.progress_frame.setLayout(progress_layout)
        layout.addWidget(self.progress_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.setMinimumSize(120, 45)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.connect_btn = QPushButton("🚀 Connect to ProtonDrive")
        self.connect_btn.setObjectName("primaryButton")
        self.connect_btn.setMinimumSize(200, 45)
        self.connect_btn.clicked.connect(self.start_configuration)
        button_layout.addWidget(self.connect_btn)
        
        layout.addLayout(button_layout)
        
        # Help link
        help_label = QLabel(
            '<a href="https://rclone.org/protondrive/" style="color: #6d4aff;">Need help? View ProtonDrive setup guide</a>'
        )
        help_label.setOpenExternalLinks(True)
        help_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(help_label)
        
        self.setLayout(layout)
    
    def _create_input_field(self, label_text: str, placeholder: str, 
                           help_text: str, is_password: bool) -> QFrame:
        """Create a modern input field with label and help text."""
        frame = QFrame()
        frame.setObjectName("inputFrame")
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Label
        label = QLabel(label_text)
        label.setObjectName("inputLabel")
        label_font = QFont()
        label_font.setPointSize(11)
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        # Input with show/hide for password
        if is_password:
            input_layout = QHBoxLayout()
            input_field = QLineEdit()
            input_field.setEchoMode(QLineEdit.Password)
            input_field.setPlaceholderText(placeholder)
            input_field.setObjectName("modernInput")
            input_field.setMinimumHeight(40)
            input_layout.addWidget(input_field)
            
            show_password = QCheckBox("Show")
            show_password.toggled.connect(
                lambda checked: input_field.setEchoMode(
                    QLineEdit.Normal if checked else QLineEdit.Password
                )
            )
            input_layout.addWidget(show_password)
            layout.addLayout(input_layout)
        else:
            input_field = QLineEdit()
            input_field.setPlaceholderText(placeholder)
            input_field.setObjectName("modernInput")
            input_field.setMinimumHeight(40)
            layout.addWidget(input_field)
        
        # Help text
        help_label = QLabel(help_text)
        help_label.setObjectName("helpText")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        frame.setLayout(layout)
        return frame
    
    def apply_modern_styling(self):
        """Apply modern, professional styling to the dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            
            #headerFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
            
            #titleLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
            }
            
            #subtitleLabel {
                color: #7f8c8d;
                font-size: 13px;
                margin-top: 5px;
            }
            
            #inputFrame, #sectionFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #e9ecef;
            }
            
            #inputLabel, #sectionHeader {
                color: #2c3e50;
                font-size: 11px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            #modernInput {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
                background-color: #ffffff;
                min-height: 40px;
            }
            
            #modernInput:focus {
                border: 2px solid #6d4aff;
                background-color: #ffffff;
            }
            
            #helpText {
                color: #6c757d;
                font-size: 11px;
                margin-top: 5px;
            }
            
            #primaryButton {
                background-color: #6d4aff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #primaryButton:hover {
                background-color: #5a3dd9;
            }
            
            #primaryButton:pressed {
                background-color: #4a2fb3;
            }
            
            #primaryButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            #secondaryButton {
                background-color: #e9ecef;
                color: #495057;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #secondaryButton:hover {
                background-color: #dee2e6;
            }
            
            #progressFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                border: 2px solid #6d4aff;
            }
            
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                text-align: center;
                height: 30px;
            }
            
            QProgressBar::chunk {
                background-color: #6d4aff;
                border-radius: 6px;
            }
            
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
                background-color: #f8f9fa;
                font-family: monospace;
                font-size: 11px;
            }
            
            QCheckBox {
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #dee2e6;
            }
            
            QCheckBox::indicator:checked {
                background-color: #6d4aff;
                border-color: #6d4aff;
            }
        """)
    
    def start_configuration(self):
        """Start the ProtonDrive configuration process."""
        # Validate inputs
        remote_name = self.remote_name_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        twofa_code = self.twofa_input.text().strip()
        otp_secret = self.otp_input.text().strip()
        
        # Validation
        if not remote_name:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a name for the ProtonDrive remote connection."
            )
            self.remote_name_input.setFocus()
            return
        
        # Check if remote already exists
        if self.rclone.remote_exists(remote_name):
            reply = QMessageBox.question(
                self,
                "Remote Already Exists",
                f"A remote named '{remote_name}' already exists.\n\n"
                "Do you want to delete it and create a new one?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # Delete existing remote
                try:
                    subprocess.run(
                        ["rclone", "config", "delete", remote_name],
                        capture_output=True,
                        timeout=10
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to delete existing remote: {str(e)}"
                    )
                    return
            else:
                return
        
        if not username:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter your ProtonDrive email address."
            )
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter your ProtonDrive password."
            )
            self.password_input.setFocus()
            return
        
        # Disable inputs and show progress
        self.set_inputs_enabled(False)
        self.progress_frame.setVisible(True)
        self.progress_text.clear()
        
        # Start configuration in background thread
        self.config_thread = RcloneConfigThread(
            username, password, twofa_code, otp_secret, remote_name, self.logger
        )
        self.config_thread.progress_update.connect(self.on_progress_update)
        self.config_thread.config_complete.connect(self.on_configuration_complete)
        self.config_thread.start()
    
    def set_inputs_enabled(self, enabled: bool):
        """Enable or disable all input fields."""
        self.remote_name_input.setEnabled(enabled)
        self.username_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.twofa_input.setEnabled(enabled)
        self.otp_input.setEnabled(enabled)
        self.connect_btn.setEnabled(enabled)
    
    def on_progress_update(self, message: str):
        """Handle progress updates from the configuration thread."""
        self.progress_label.setText(message)
        self.progress_text.append(message)
    
    def on_configuration_complete(self, success: bool, message: str):
        """Handle configuration completion."""
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1 if success else 0)
        
        if success:
            QMessageBox.information(
                self,
                "Success!",
                f"<h3>🎉 ProtonDrive configured successfully!</h3>"
                f"<p>{message}</p>"
                "<p>You can now proceed with setting up your sync folders.</p>"
            )
            # Test the connection
            remote_name = self.remote_name_input.text().strip()
            test_success, test_message = self.rclone.test_remote(remote_name)
            if test_success:
                self.progress_text.append("\n✅ Connection test successful!")
                self.accept()  # Close dialog with success
            else:
                self.progress_text.append(f"\n⚠️ Connection test failed: {test_message}")
                QMessageBox.warning(
                    self,
                    "Connection Test Failed",
                    f"<p>ProtonDrive was configured but the connection test failed:</p>"
                    f"<p><b>{test_message}</b></p>"
                    "<p>Please check your credentials and try again.</p>"
                )
                self.set_inputs_enabled(True)
                self.progress_frame.setVisible(False)
        else:
            QMessageBox.critical(
                self,
                "Configuration Failed",
                f"<h3>❌ Failed to configure ProtonDrive</h3>"
                f"<p>{message}</p>"
                "<p>Please check your credentials and try again.</p>"
            )
            self.set_inputs_enabled(True)
            self.progress_frame.setVisible(False)
