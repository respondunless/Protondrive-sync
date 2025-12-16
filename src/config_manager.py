"""Configuration management for ProtonDrive Sync."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration."""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".config" / "protondrive-sync"
    CONFIG_FILE = "config.json"
    
    DEFAULT_CONFIG = {
        "rclone_remote": "",
        "local_folder": "",
        "auto_sync_enabled": False,
        "sync_interval_minutes": 30,
        "first_run": True,
        "notifications_enabled": True,
        "log_level": "INFO"
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the configuration manager.
        
        Args:
            config_dir: Optional custom configuration directory
        """
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self.config_file_path = self.config_dir / self.CONFIG_FILE
        self.config: Dict[str, Any] = {}
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create config
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default.
        
        Returns:
            Dictionary containing configuration
        """
        if self.config_file_path.exists():
            try:
                with open(self.config_file_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.config = {**self.DEFAULT_CONFIG, **loaded_config}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
        
        return self.config
    
    def save_config(self) -> bool:
        """Save current configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values.
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        self.config.update(updates)
    
    def is_first_run(self) -> bool:
        """Check if this is the first run.
        
        Returns:
            True if first run, False otherwise
        """
        return self.config.get("first_run", True)
    
    def mark_setup_complete(self) -> None:
        """Mark the first-run setup as complete."""
        self.config["first_run"] = False
        self.save_config()
    
    def is_configured(self) -> bool:
        """Check if the application is properly configured.
        
        Returns:
            True if configured, False otherwise
        """
        return (
            bool(self.config.get("rclone_remote")) and
            bool(self.config.get("local_folder"))
        )
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
