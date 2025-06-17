"""
Configuration Management Module
Handles all application configuration settings and validation
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Union, Optional

from yaml import load, FullLoader


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors"""
    pass


class ConfigManager:
    """Modern configuration management with validation and type hints"""
    
    _instance: Optional['ConfigManager'] = None
    _config_data: Dict[str, Any] = {}
    
    def __new__(cls) -> 'ConfigManager':
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager"""
        if not hasattr(self, '_initialized'):
            self._load_configuration()
            self._initialized = True
    
    def _load_configuration(self) -> None:
        """Load configuration from YAML files"""
        user_config_path = Path(f"{os.getcwd()}/myConfig.yaml")
        default_config_path = Path(f"{os.getcwd()}/config.yaml")
        
        config_path = None
        if user_config_path.exists():
            config_path = user_config_path
        elif default_config_path.exists():
            config_path = default_config_path
        else:
            raise ConfigurationError("Configuration file not found. Please ensure either myConfig.yaml or config.yaml exists.")
        
        try:
            with open(config_path, encoding="utf-8") as file:
                self._config_data = load(file, Loader=FullLoader)
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file: {e}")
    
    def get_config(self, section: Optional[str] = None, key: Optional[str] = None) -> Union[Dict[str, Any], str, int, bool]:
        """
        Get configuration value(s)
        
        Args:
            section: Configuration section name
            key: Configuration key within section
            
        Returns:
            Configuration value or section
            
        Raises:
            ConfigurationError: If section or key not found
        """
        if not section:
            return self._config_data
        
        if section not in self._config_data:
            raise ConfigurationError(f"Configuration section '{section}' not found")
        
        if not key:
            return self._config_data[section]
        
        if key not in self._config_data[section]:
            raise ConfigurationError(f"Configuration key '{key}' not found in section '{section}'")
        
        return self._config_data[section][key]
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.get_config('Database')
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return self.get_config('Redis')
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask configuration"""
        return self.get_config('Flask')
    
    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration"""
        return self.get_config('E-Mail')
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """Get specific API configuration"""
        return self.get_config(api_name)


class TimeManager:
    """Handle time-related operations with timezone awareness"""
    
    HOST_TIMEZONE_OFFSET = 0  # UTC+0
    CLIENT_TIMEZONE_OFFSETS = {'zh-CN': 8, 'en-US': -5}  # UTC offsets for different regions
    
    @classmethod
    def get_client_current_time(cls, region: str = "zh-CN", time_format: str = "datetime") -> str:
        """
        Get current time for client timezone
        
        Args:
            region: Client region code
            time_format: Format type - 'datetime', 'date', or 'time'
            
        Returns:
            Formatted time string
            
        Raises:
            ValueError: If invalid format or region
        """
        if region not in cls.CLIENT_TIMEZONE_OFFSETS:
            raise ValueError(f"Unsupported region: {region}")
        
        server_time = datetime.utcnow()
        client_time = server_time + timedelta(hours=cls.CLIENT_TIMEZONE_OFFSETS[region])
        
        format_map = {
            "datetime": "%Y-%m-%d %H:%M:%S",
            "date": "%Y-%m-%d",
            "time": "%H:%M:%S"
        }
        
        if time_format not in format_map:
            raise ValueError(f"Invalid time format: {time_format}")
        
        return client_time.strftime(format_map[time_format])
    
    @classmethod
    def convert_to_client_time(cls, server_time: datetime, region: str = "zh-CN") -> datetime:
        """Convert server time to client timezone"""
        if region not in cls.CLIENT_TIMEZONE_OFFSETS:
            raise ValueError(f"Unsupported region: {region}")
        
        return server_time + timedelta(hours=cls.CLIENT_TIMEZONE_OFFSETS[region])


# Global configuration instance
config_manager = ConfigManager()

# Convenience function for backward compatibility
def get_configuration(section: Optional[str] = None, key: Optional[str] = None) -> Union[Dict[str, Any], str, int, bool]:
    """
    Get configuration value - convenience function
    
    Args:
        section: Configuration section name
        key: Configuration key within section
        
    Returns:
        Configuration value or section
    """
    return config_manager.get_config(section, key) 