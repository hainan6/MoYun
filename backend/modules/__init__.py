"""
核心业务模块包
============

本包包含应用程序的核心业务逻辑模块。

模块列表:
    - file_manager: 文件系统管理模块
    - network_services: 网络服务模块
    - image_processor: 图像处理模块

主要功能:
    - 文件管理
    - 邮件服务
    - 外部API调用
    - 图像处理
"""

from .file_manager import FileSystemManager, AssetType
from .network_services import EmailService, ExternalAPIService
from .image_processor import ImageProcessor, AlignmentOption

# 定义包的公共API
__all__ = [
    'FileSystemManager',    # 文件系统管理器
    'AssetType',           # 资源类型枚举
    'EmailService',        # 邮件服务
    'ExternalAPIService',  # 外部API服务
    'ImageProcessor',      # 图像处理器
    'AlignmentOption'      # 对齐选项枚举
] 