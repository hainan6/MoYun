"""
配置管理包
========

本包负责处理应用程序配置和设置。

主要功能:
    - 配置文件管理
    - 配置项读取和验证
    - 时间管理
    - 全局设置管理
"""

from .settings import config_manager, get_configuration, TimeManager, ConfigManager

# 定义包的公共API
__all__ = [
    'config_manager',      # 配置管理器实例
    'get_configuration',   # 获取配置的函数
    'TimeManager',        # 时间管理器类
    'ConfigManager'       # 配置管理器类
] 