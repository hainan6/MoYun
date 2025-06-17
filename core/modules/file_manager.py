"""
File Management Module
Handles all file operations including storage, retrieval, and management
"""
import os
from enum import Enum
from pathlib import Path
from typing import Tuple, Optional
from os import remove

from core.config.settings import config_manager


class FileTypeError(Exception):
    """Custom exception for file type related errors"""
    pass


class StoragePathError(Exception):
    """Custom exception for storage path related errors"""
    pass


class AssetType(Enum):
    """
    Asset type enumeration
    Values must match folder names in static directory
    """
    BOOK_COVER = "bookCover"
    JOURNAL_HEADER = "journalHeader"
    PROFILE_PHOTO = "profilePhoto"
    GROUP_ICON = "groupIcon"
    ERROR_IMAGE = "errorImage"


class FileSystemManager:
    """
    Modern file system management with improved error handling and type safety
    """
    
    def __init__(self):
        """Initialize file system manager"""
        self._project_root: Path = Path(os.getcwd())
        self._static_directory: Path = self._get_static_directory()
        self._validate_storage_structure()
    
    def _get_static_directory(self) -> Path:
        """Get and validate static directory path"""
        try:
            storage_path = config_manager.get_config("Path", "StoragePath")
            static_dir = Path(str(self._project_root) + storage_path)
            
            if not static_dir.exists():
                raise StoragePathError(f"Static directory not found: {static_dir}")
            
            return static_dir
        except Exception as e:
            raise StoragePathError(f"Failed to initialize static directory: {e}")
    
    def _validate_storage_structure(self) -> None:
        """Validate that all required asset directories exist"""
        for asset_type in AssetType:
            asset_dir = self._static_directory / asset_type.value
            if not asset_dir.exists():
                # Create missing directories
                asset_dir.mkdir(parents=True, exist_ok=True)
    
    def _resolve_file_paths(
        self, 
        asset_type: AssetType, 
        pattern: Optional[str] = None, 
        use_default: bool = False
    ) -> Tuple[str, str]:
        """
        Resolve file paths for given asset type and pattern
        
        Args:
            asset_type: Type of asset to find
            pattern: File name pattern (e.g., "1.*" for files like "1.jpg")
            use_default: Whether to return default file if pattern not found
            
        Returns:
            Tuple of (absolute_path, relative_path)
            
        Raises:
            FileTypeError: If asset directory not found
        """
        asset_directory: Path = self._static_directory / asset_type.value
        
        if not asset_directory.exists():
            raise FileTypeError(f"Asset directory not found: {asset_directory}")
        
        absolute_path = ""
        relative_path = ""
        
        # Try to find file matching pattern
        if pattern:
            matching_files = list(asset_directory.glob(pattern))
            if matching_files:
                absolute_path = matching_files[0].as_posix()
                relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        
        # Use default file if pattern not found and default is enabled
        if not absolute_path and use_default:
            default_file = asset_directory / "default.webp"
            if default_file.exists():
                absolute_path = default_file.as_posix()
                relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        
        return absolute_path, relative_path
    
    # Book Cover Management
    def get_book_cover_path(
        self, 
        book_id: int, 
        return_absolute: bool = False, 
        use_default: bool = True
    ) -> str:
        """
        Get book cover file path
        
        Args:
            book_id: Book identifier
            return_absolute: Whether to return absolute path
            use_default: Whether to use default cover if specific not found
            
        Returns:
            File path string
        """
        absolute_path, relative_path = self._resolve_file_paths(
            AssetType.BOOK_COVER, 
            f"{book_id}.*", 
            use_default
        )
        return absolute_path if return_absolute else relative_path
    
    def generate_book_cover_path(self, book_id: int, return_absolute: bool = False) -> str:
        """
        Generate path where book cover should be stored
        
        Args:
            book_id: Book identifier
            return_absolute: Whether to return absolute path
            
        Returns:
            Generated file path
        """
        absolute_path = (self._static_directory / AssetType.BOOK_COVER.value / f"{book_id}.jpg").as_posix()
        relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        return absolute_path if return_absolute else relative_path
    
    # Journal Header Management
    def get_journal_header_path(
        self, 
        journal_id: int, 
        return_absolute: bool = False, 
        use_default: bool = True
    ) -> str:
        """Get journal header image path"""
        absolute_path, relative_path = self._resolve_file_paths(
            AssetType.JOURNAL_HEADER, 
            f"{journal_id}.*", 
            use_default
        )
        return absolute_path if return_absolute else relative_path
    
    def generate_journal_header_path(self, journal_id: int, return_absolute: bool = False) -> str:
        """Generate path where journal header should be stored"""
        absolute_path = (self._static_directory / AssetType.JOURNAL_HEADER.value / f"{journal_id}.jpg").as_posix()
        relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        return absolute_path if return_absolute else relative_path
    
    def delete_journal_header(self, journal_id: int) -> bool:
        """
        Delete journal header image
        
        Args:
            journal_id: Journal identifier
            
        Returns:
            True if deleted successfully, False if file not found
        """
        absolute_path, _ = self._resolve_file_paths(AssetType.JOURNAL_HEADER, f"{journal_id}.*")
        if absolute_path and Path(absolute_path).exists():
            remove(absolute_path)
            return True
        return False
    
    # Profile Photo Management
    def get_profile_photo_path(
        self, 
        user_id: int, 
        return_absolute: bool = False, 
        use_default: bool = True
    ) -> str:
        """Get user profile photo path"""
        absolute_path, relative_path = self._resolve_file_paths(
            AssetType.PROFILE_PHOTO, 
            f"{user_id}.*", 
            use_default
        )
        return absolute_path if return_absolute else relative_path
    
    def generate_profile_photo_path(self, user_id: int, return_absolute: bool = False) -> str:
        """Generate path where profile photo should be stored"""
        absolute_path = (self._static_directory / AssetType.PROFILE_PHOTO.value / f"{user_id}.jpg").as_posix()
        relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        return absolute_path if return_absolute else relative_path
    
    def delete_profile_photo(self, user_id: int) -> bool:
        """Delete user profile photo"""
        absolute_path, _ = self._resolve_file_paths(AssetType.PROFILE_PHOTO, f"{user_id}.*")
        if absolute_path and Path(absolute_path).exists():
            remove(absolute_path)
            return True
        return False
    
    # Group Icon Management
    def get_group_icon_path(
        self, 
        group_id: int, 
        return_absolute: bool = False, 
        use_default: bool = True
    ) -> str:
        """Get group icon path"""
        absolute_path, relative_path = self._resolve_file_paths(
            AssetType.GROUP_ICON, 
            f"{group_id}.*", 
            use_default
        )
        return absolute_path if return_absolute else relative_path
    
    def generate_group_icon_path(self, group_id: int, return_absolute: bool = False) -> str:
        """Generate path where group icon should be stored"""
        absolute_path = (self._static_directory / AssetType.GROUP_ICON.value / f"{group_id}.jpg").as_posix()
        relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        return absolute_path if return_absolute else relative_path
    
    def delete_group_icon(self, group_id: int) -> bool:
        """Delete group icon"""
        absolute_path, _ = self._resolve_file_paths(AssetType.GROUP_ICON, f"{group_id}.*")
        if absolute_path and Path(absolute_path).exists():
            remove(absolute_path)
            return True
        return False
    
    # Error Image Management
    def get_error_image_path(self, error_code: int, return_absolute: bool = False) -> str:
        """Get error page image path"""
        absolute_path, relative_path = self._resolve_file_paths(
            AssetType.ERROR_IMAGE, 
            f"{error_code}.*"
        )
        return absolute_path if return_absolute else relative_path
    
    # General Utility Methods
    def get_absolute_path(self, relative_path: str) -> str:
        """
        Convert relative path to absolute path
        
        Args:
            relative_path: Relative file path
            
        Returns:
            Absolute file path
        """
        if os.path.isabs(relative_path):
            return relative_path
        return (self._project_root / relative_path).as_posix()
    
    def get_relative_path(self, absolute_path: str) -> str:
        """
        Convert absolute path to relative path
        
        Args:
            absolute_path: Absolute file path
            
        Returns:
            Relative file path
        """
        return os.path.relpath(absolute_path, self._project_root)
    
    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensure that a directory exists, create if it doesn't
        
        Args:
            directory_path: Directory path to check/create
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to create directory {directory_path}: {e}")
            return False 