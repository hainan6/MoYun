"""
MoYun 阅读平台核心包
====================

本模块包含 MoYun 阅读平台的所有核心功能实现。

模块结构:
    - config: 配置管理模块
    - modules: 核心功能模块
    - handlers: 请求处理器
    - data: 数据模型和数据访问层

主要组件:
    - 配置管理 (config_manager, get_configuration)
    - 时间管理 (TimeManager)
    - 文件系统管理 (FileSystemManager)
    - 网络服务 (EmailService, ExternalAPIService)
    - 图像处理 (ImageProcessor)

版本: 1.0.0
作者: MoYun Team
"""

# 从配置模块导入配置管理相关组件
from .config.settings import config_manager, get_configuration, TimeManager

# 从文件管理模块导入文件系统管理器和资源类型枚举
from .modules.file_manager import FileSystemManager, AssetType

# 从网络服务模块导入邮件服务和外部API服务
from .modules.network_services import EmailService, ExternalAPIService

# 从图像处理模块导入图像处理器和对齐选项
from .modules.image_processor import ImageProcessor, AlignmentOption

# 定义此包的公共API
__all__ = [
    'config_manager',      # 配置管理器实例
    'get_configuration',   # 获取配置的函数
    'TimeManager',        # 时间管理器类
    'FileSystemManager',  # 文件系统管理器类
    'AssetType',         # 资源类型枚举
    'EmailService',      # 邮件服务类
    'ExternalAPIService', # 外部API服务类
    'ImageProcessor',    # 图像处理器类
    'AlignmentOption'    # 对齐选项枚举
] 