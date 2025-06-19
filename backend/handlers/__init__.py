"""
请求处理器包
==========

本包包含应用程序的所有请求处理器。

模块结构:
    - base_handler: 基础处理器类
    - auth_handler: 认证处理器类
    - home_handler: 主页处理器类

兼容性说明:
    本模块同时支持新的处理器架构和旧的服务层架构，
    通过兼容性包装器实现平滑过渡。

主要功能:
    - 路由注册
    - 请求处理
    - 响应生成
    - 安全中间件配置
"""

from .base_handler import BaseHandler
from .auth_handler import AuthenticationHandler

# 导入旧服务层组件（兼容性导入）
try:
    from service.response.BookPage import bookResponse
    from service.response.ChatPage import chatResponse  
    from service.response.HomePage import homepageResponse
    from service.response.ErrorPage import errorResponse
    from service.response.JournalPage import journalResponse
    from service.response.LLMPage import lLMResponse
    from service.response.ProfilePage import profileResponse
    from service.response.GroupPage import groupResponse
    from service.response.SearchPage import searchResponse
    from service.response.MessagePage import messageResponse
    from service.response._Utils import securityCheck
except ImportError as e:
    print(f"警告: 旧服务层导入失败: {e}")


def register_authentication_routes(app, file_manager, database_manager, email_service):
    """
    注册认证相关路由
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
        email_service: 邮件服务实例
        
    说明:
        使用新的处理器架构注册认证路由
    """
    auth_handler = AuthenticationHandler(database_manager, file_manager, email_service)
    auth_handler.register_routes(app)


def register_book_routes(app, file_manager, database_manager):
    """
    注册图书相关路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
    """
    try:
        bookResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"警告: 图书路由注册失败: {e}")


def register_chat_routes(app, file_manager, database_manager):
    """
    注册聊天相关路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
    """
    try:
        chatResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"警告: 聊天路由注册失败: {e}")


def register_homepage_routes(app, file_manager, database_manager, api_service):
    """
    注册主页相关路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
        api_service: API服务实例
    """
    try:
        homepageResponse(app, file_manager, database_manager, api_service)
    except Exception as e:
        print(f"警告: 主页路由注册失败: {e}")


def register_error_routes(app, file_manager, database_manager):
    """
    注册错误处理路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
    """
    try:
        errorResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"警告: 错误处理路由注册失败: {e}")


def register_journal_routes(app, file_manager, database_manager):
    """
    注册日志相关路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
    """
    try:
        journalResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"警告: 日志路由注册失败: {e}")


def register_ai_routes(app, api_service):
    """
    注册AI相关路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        api_service: API服务实例
    """
    try:
        lLMResponse(app, api_service)
    except Exception as e:
        print(f"警告: AI路由注册失败: {e}")


def register_profile_routes(app, file_manager, database_manager):
    """
    注册用户档案相关路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
    """
    try:
        profileResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"警告: 用户档案路由注册失败: {e}")


def register_group_routes(app, file_manager, database_manager):
    """
    注册群组相关路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
    """
    try:
        groupResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"警告: 群组路由注册失败: {e}")


def register_search_routes(app, file_manager, database_manager):
    """
    注册搜索相关路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
    """
    try:
        searchResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"警告: 搜索路由注册失败: {e}")


def register_message_routes(app, file_manager, database_manager):
    """
    注册消息相关路由（兼容性包装）
    
    参数:
        app: Flask应用实例
        file_manager: 文件管理器实例
        database_manager: 数据库管理器实例
    """
    try:
        messageResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"警告: 消息路由注册失败: {e}")


def configure_security_middleware(app):
    """
    配置安全中间件（兼容性包装）
    
    参数:
        app: Flask应用实例
        
    说明:
        配置应用程序的安全相关中间件
    """
    try:
        securityCheck(app)
    except Exception as e:
        print(f"警告: 安全中间件配置失败: {e}")


# 定义包的公共API
__all__ = [
    'BaseHandler',           # 基础处理器类
    'AuthenticationHandler', # 认证处理器类
    'register_authentication_routes',  # 注册认证路由
    'register_book_routes',           # 注册图书路由
    'register_chat_routes',           # 注册聊天路由
    'register_homepage_routes',       # 注册主页路由
    'register_error_routes',          # 注册错误处理路由
    'register_journal_routes',        # 注册日志路由
    'register_ai_routes',             # 注册AI路由
    'register_profile_routes',        # 注册用户档案路由
    'register_group_routes',          # 注册群组路由
    'register_search_routes',         # 注册搜索路由
    'register_message_routes',        # 注册消息路由
    'configure_security_middleware'   # 配置安全中间件
] 