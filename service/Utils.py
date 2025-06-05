"""通用工具服务"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union

from yaml import load, FullLoader

DEFAULT_CONFIG_PATH = Path(f"{os.getcwd()}/myConfig.yaml")
PROJECT_CONFIG_PATH = Path(f"{os.getcwd()}/config.yaml")

if DEFAULT_CONFIG_PATH.exists():
    config_path = DEFAULT_CONFIG_PATH
elif PROJECT_CONFIG_PATH.exists():
    config_path = PROJECT_CONFIG_PATH
else:
    raise FileNotFoundError("config file not found")
with open(config_path, encoding="utf-8") as f:
    Config: dict = load(f, Loader=FullLoader)


def queryConfig(category: str = None, key: str = None) -> dict or Union[str, int]:
    """
    获取配置文件中特定的配置项(优先读取myConfig.yaml，若不存在则读取config.yaml)
    :param category: 配置项类别
    :param key: 配置项key
    :return:
    """
    if not category:
        return Config
    elif category not in Config:
        raise ValueError(f"Parameter category {category} not found")
    else:
        if not key:
            return Config[category]
        elif key not in Config[category]:
            raise ValueError(f"Parameter key {key} not found")
        else:
            return Config[category][key]


class Time:
    """使用该类处理时间的目的是应对服务器和客户端时区不同的情况。"""
    _host_time_zone = 0  # UTC+0
    _client_time_zone = {'zh-CN': 8}  # UTC+8，东8区

    @classmethod
    def getClientNow(cls, region: str = "zh-CN", time_format: str = "datetime") -> str:
        """
        获取客户端当前时间
        :param region: 地区
        :param time_format: 时间格式
        :return:
        """
        host_now = datetime.utcnow()  # 服务器时间
        client_now = host_now + timedelta(hours=cls._client_time_zone[region])  # 客户端时间
        if time_format == "datetime":
            return client_now.now().strftime("%Y-%m-%d %H:%M:%S")
        elif time_format == "date":
            return client_now.now().strftime("%Y-%m-%d")
        elif time_format == "time":
            return client_now.now().strftime("%H:%M:%S")
        else:
            raise Exception("Invalid format")
