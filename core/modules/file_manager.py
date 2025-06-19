"""
文件管理模块
==========

本模块负责处理所有文件操作，包括存储、检索和管理。

主要功能:
    - 文件存储和检索
    - 资源类型管理
    - 路径解析和验证
    - 目录结构维护

依赖:
    - os: 操作系统接口
    - pathlib: 路径处理
    - core.config: 配置管理
"""

import os
from enum import Enum
from pathlib import Path
from typing import Tuple, Optional
from os import remove

from core.config.settings import config_manager


class FileTypeError(Exception):
    """文件类型相关的自定义异常"""
    pass


class StoragePathError(Exception):
    """存储路径相关的自定义异常"""
    pass


class AssetType(Enum):
    """
    资源类型枚举
    
    说明:
        枚举值必须与静态目录中的文件夹名称匹配
        
    枚举值:
        BOOK_COVER: 图书封面
        JOURNAL_HEADER: 日志头图
        PROFILE_PHOTO: 用户头像
        GROUP_ICON: 群组图标
        ERROR_IMAGE: 错误提示图
    """
    BOOK_COVER = "bookCover"
    JOURNAL_HEADER = "journalHeader"
    PROFILE_PHOTO = "profilePhoto"
    GROUP_ICON = "groupIcon"
    ERROR_IMAGE = "errorImage"


class FileSystemManager:
    """
    现代化的文件系统管理器，提供改进的错误处理和类型安全
    
    主要职责:
        1. 管理文件存储结构
        2. 处理文件路径解析
        3. 提供资源访问接口
        4. 维护存储目录结构
        
    设计特点:
        - 类型安全：使用枚举限制资源类型
        - 错误处理：提供详细的异常信息
        - 路径管理：统一处理相对和绝对路径
    """
    
    def __init__(self):
        """
        初始化文件系统管理器
        
        初始化步骤:
            1. 确定项目根目录
            2. 获取静态文件目录
            3. 验证存储结构
        """
        self._project_root: Path = Path(os.getcwd())
        self._static_directory: Path = self._get_static_directory()
        self._validate_storage_structure()
    
    def _get_static_directory(self) -> Path:
        """
        获取并验证静态文件目录路径
        
        返回:
            静态文件目录的Path对象
            
        异常:
            StoragePathError: 当静态目录不存在或初始化失败时
        """
        try:
            storage_path = config_manager.get_config("Path", "StoragePath")
            static_dir = Path(str(self._project_root) + storage_path)
            
            if not static_dir.exists():
                raise StoragePathError(f"静态文件目录未找到: {static_dir}")
            
            return static_dir
        except Exception as e:
            raise StoragePathError(f"静态文件目录初始化失败: {e}")
    
    def _validate_storage_structure(self) -> None:
        """
        验证所有必需的资源目录是否存在
        
        说明:
            - 检查每种资源类型的目录
            - 如果目录不存在则创建
        """
        for asset_type in AssetType:
            asset_dir = self._static_directory / asset_type.value
            if not asset_dir.exists():
                # 创建缺失的目录
                asset_dir.mkdir(parents=True, exist_ok=True)
    
    def _resolve_file_paths(
        self, 
        asset_type: AssetType, 
        pattern: Optional[str] = None, 
        use_default: bool = False
    ) -> Tuple[str, str]:
        """
        解析指定资源类型和模式的文件路径
        
        参数:
            asset_type: 资源类型
            pattern: 文件名模式（如 "1.*" 匹配 "1.jpg"）
            use_default: 是否在未找到文件时返回默认文件
            
        返回:
            (绝对路径, 相对路径) 的元组
            
        异常:
            FileTypeError: 当资源目录不存在时
        """
        asset_directory: Path = self._static_directory / asset_type.value
        
        if not asset_directory.exists():
            raise FileTypeError(f"资源目录未找到: {asset_directory}")
        
        absolute_path = ""
        relative_path = ""
        
        # 尝试查找匹配模式的文件
        if pattern:
            matching_files = list(asset_directory.glob(pattern))
            if matching_files:
                absolute_path = matching_files[0].as_posix()
                relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        
        # 如果未找到文件且启用默认值，则使用默认文件
        if not absolute_path and use_default:
            default_file = asset_directory / "default.webp"
            if default_file.exists():
                absolute_path = default_file.as_posix()
                relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        
        return absolute_path, relative_path
    
    # 图书封面管理
    def get_book_cover_path(
        self, 
        book_id: int, 
        return_absolute: bool = False, 
        use_default: bool = True
    ) -> str:
        """
        获取图书封面文件路径
        
        参数:
            book_id: 图书ID
            return_absolute: 是否返回绝对路径
            use_default: 是否在未找到时使用默认封面
            
        返回:
            文件路径字符串
        """
        absolute_path, relative_path = self._resolve_file_paths(
            AssetType.BOOK_COVER, 
            f"{book_id}.*", 
            use_default
        )
        return absolute_path if return_absolute else relative_path
    
    def generate_book_cover_path(self, book_id: int, return_absolute: bool = False) -> str:
        """
        生成图书封面的存储路径
        
        参数:
            book_id: 图书ID
            return_absolute: 是否返回绝对路径
            
        返回:
            生成的文件路径
        """
        absolute_path = (self._static_directory / AssetType.BOOK_COVER.value / f"{book_id}.jpg").as_posix()
        relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        return absolute_path if return_absolute else relative_path
    
    # 日志头图管理
    def get_journal_header_path(
        self, 
        journal_id: int, 
        return_absolute: bool = False, 
        use_default: bool = True
    ) -> str:
        """
        获取日志头图路径
        
        参数:
            journal_id: 日志ID
            return_absolute: 是否返回绝对路径
            use_default: 是否在未找到时使用默认图片
            
        返回:
            文件路径字符串
        """
        absolute_path, relative_path = self._resolve_file_paths(
            AssetType.JOURNAL_HEADER, 
            f"{journal_id}.*", 
            use_default
        )
        return absolute_path if return_absolute else relative_path
    
    def generate_journal_header_path(self, journal_id: int, return_absolute: bool = False) -> str:
        """
        生成日志头图的存储路径
        
        参数:
            journal_id: 日志ID
            return_absolute: 是否返回绝对路径
            
        返回:
            生成的文件路径
        """
        absolute_path = (self._static_directory / AssetType.JOURNAL_HEADER.value / f"{journal_id}.jpg").as_posix()
        relative_path = absolute_path.replace(self._project_root.as_posix(), "")
        return absolute_path if return_absolute else relative_path
    
    def delete_journal_header(self, journal_id: int) -> bool:
        """
        删除日志头图
        
        参数:
            journal_id: 日志ID
            
        返回:
            删除成功返回True，文件不存在返回False
        """
        absolute_path, _ = self._resolve_file_paths(AssetType.JOURNAL_HEADER, f"{journal_id}.*")
        if absolute_path and Path(absolute_path).exists():
            remove(absolute_path)
            return True
        return False
    
    # 用户头像管理
    def get_profile_photo_path(
        self, 
        user_id: int, 
        return_absolute: bool = False, 
        use_default: bool = True
    ) -> str:
        """
        获取用户头像路径
        
        参数:
            user_id: 用户ID
            return_absolute: 是否返回绝对路径
            use_default: 是否在未找到时使用默认头像
            
        返回:
            文件路径字符串
        """
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