"""
Core Package
Contains all core functionality for the MoYun reading platform
"""

from .config.settings import config_manager, get_configuration, TimeManager
from .modules.file_manager import FileSystemManager, AssetType
from .modules.network_services import EmailService, ExternalAPIService
from .modules.image_processor import ImageProcessor, AlignmentOption

__all__ = [
    'config_manager',
    'get_configuration', 
    'TimeManager',
    'FileSystemManager',
    'AssetType',
    'EmailService',
    'ExternalAPIService', 
    'ImageProcessor',
    'AlignmentOption'
] 