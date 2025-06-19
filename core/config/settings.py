"""
配置管理模块
处理所有应用程序配置设置和验证
包含配置管理器和时间管理器两个主要类
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Union, Optional

from yaml import load, FullLoader


class ConfigurationError(Exception):
    """配置相关的自定义异常类"""
    pass


class ConfigManager:
    """现代化的配置管理器，提供验证和类型提示
    
    实现了单例模式，确保全局只有一个配置管理器实例
    支持从YAML文件加载配置
    提供类型安全的配置访问方法
    """
    
    _instance: Optional['ConfigManager'] = None  # 单例实例
    _config_data: Dict[str, Any] = {}  # 存储配置数据的字典
    
    def __new__(cls) -> 'ConfigManager':
        """实现单例模式，确保只创建一个ConfigManager实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器
        
        只在第一次创建实例时加载配置文件
        """
        if not hasattr(self, '_initialized'):
            self._load_configuration()
            self._initialized = True
    
    def _load_configuration(self) -> None:
        """从YAML文件加载配置
        
        优先加载 myConfig.yaml，如果不存在则加载 config.yaml
        如果两个文件都不存在则抛出异常
        """
        user_config_path = Path(f"{os.getcwd()}/myConfig.yaml")
        default_config_path = Path(f"{os.getcwd()}/config.yaml")
        
        config_path = None
        if user_config_path.exists():
            config_path = user_config_path
        elif default_config_path.exists():
            config_path = default_config_path
        else:
            raise ConfigurationError("未找到配置文件。请确保 myConfig.yaml 或 config.yaml 存在。")
        
        try:
            with open(config_path, encoding="utf-8") as file:
                self._config_data = load(file, Loader=FullLoader)
        except Exception as e:
            raise ConfigurationError(f"加载配置文件失败: {e}")
    
    def get_config(self, section: Optional[str] = None, key: Optional[str] = None) -> Union[Dict[str, Any], str, int, bool]:
        """获取配置值
        
        Args:
            section: 配置节名称
            key: 配置节中的键名
            
        Returns:
            配置值或配置节
            
        Raises:
            ConfigurationError: 如果节或键不存在
        """
        if not section:
            return self._config_data
        
        if section not in self._config_data:
            raise ConfigurationError(f"配置节 '{section}' 不存在")
        
        if not key:
            return self._config_data[section]
        
        if key not in self._config_data[section]:
            raise ConfigurationError(f"配置键 '{key}' 在节 '{section}' 中不存在")
        
        return self._config_data[section][key]
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.get_config('Database')
    
    def get_redis_config(self) -> Dict[str, Any]:
        """获取Redis配置"""
        return self.get_config('Redis')
    
    def get_flask_config(self) -> Dict[str, Any]:
        """获取Flask配置"""
        return self.get_config('Flask')
    
    def get_email_config(self) -> Dict[str, Any]:
        """获取邮件配置"""
        return self.get_config('E-Mail')
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """获取特定API的配置"""
        return self.get_config(api_name)


class TimeManager:
    """处理与时区相关的时间操作
    
    提供服务器时间和客户端时间之间的转换
    支持多个地区的时区偏移
    """
    
    HOST_TIMEZONE_OFFSET = 0  # UTC+0，服务器使用UTC时间
    CLIENT_TIMEZONE_OFFSETS = {'zh-CN': 8, 'en-US': -5}  # 不同地区的UTC时差
    
    @classmethod
    def get_client_current_time(cls, region: str = "zh-CN", time_format: str = "datetime") -> str:
        """获取客户端当前时间
        
        Args:
            region: 客户端地区代码
            time_format: 时间格式 - 'datetime'（日期时间）, 'date'（日期）, 或 'time'（时间）
            
        Returns:
            格式化的时间字符串
            
        Raises:
            ValueError: 如果格式或地区无效
        """
        if region not in cls.CLIENT_TIMEZONE_OFFSETS:
            raise ValueError(f"不支持的地区: {region}")
        
        server_time = datetime.utcnow()
        client_time = server_time + timedelta(hours=cls.CLIENT_TIMEZONE_OFFSETS[region])
        
        format_map = {
            "datetime": "%Y-%m-%d %H:%M:%S",
            "date": "%Y-%m-%d",
            "time": "%H:%M:%S"
        }
        
        if time_format not in format_map:
            raise ValueError(f"无效的时间格式: {time_format}")
        
        return client_time.strftime(format_map[time_format])
    
    @classmethod
    def convert_to_client_time(cls, server_time: datetime, region: str = "zh-CN") -> datetime:
        """将服务器时间转换为客户端时区时间"""
        if region not in cls.CLIENT_TIMEZONE_OFFSETS:
            raise ValueError(f"不支持的地区: {region}")
        
        return server_time + timedelta(hours=cls.CLIENT_TIMEZONE_OFFSETS[region])


# 全局配置管理器实例
config_manager = ConfigManager()

# 为了向后兼容提供的便捷函数
def get_configuration(section: Optional[str] = None, key: Optional[str] = None) -> Union[Dict[str, Any], str, int, bool]:
    """
    获取配置值的便捷函数
    
    Args:
        section: 配置节名称
        key: 配置节中的键名
        
    Returns:
        配置值或配置节
    """
    return config_manager.get_config(section, key) 