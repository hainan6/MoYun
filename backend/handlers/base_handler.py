"""
基础请求处理器模块
================

本模块提供了所有请求处理器的基础功能实现。

主要功能:
    - 用户认证和授权
    - 会话管理
    - 表单数据处理
    - 消息闪现
    - 模板渲染
    - 数据库操作异常处理
    - 分页参数处理

依赖:
    - flask: Web框架
    - core.data: 数据库管理
    - core.modules.file_manager: 文件系统管理
"""

from typing import Optional, Dict, Any, Union
from flask import session, request, flash, redirect, url_for, render_template
from functools import wraps

from core.data import DatabaseManager, UserData
from core.modules.file_manager import FileSystemManager


class HandlerError(Exception):
    """处理器相关的自定义异常类"""
    pass


class BaseHandler:
    """
    基础处理器类，为所有路由处理器提供通用功能
    
    主要职责:
        1. 用户认证和会话管理
        2. 请求数据处理和验证
        3. 用户消息管理
        4. 视图渲染
        5. 数据库操作
        6. 文件系统操作
    """
    
    def __init__(self, database_manager: DatabaseManager, file_manager: FileSystemManager):
        """
        初始化基础处理器
        
        参数:
            database_manager: 数据库管理器实例
            file_manager: 文件管理器实例
        """
        self.db = database_manager
        self.file_manager = file_manager
    
    def get_current_user(self) -> Optional[UserData]:
        """
        获取当前登录用户信息
        
        返回:
            当前用户数据，如未登录则返回 None
        """
        return session.get("login_user")
    
    def is_authenticated(self) -> bool:
        """
        检查用户是否已认证
        
        返回:
            如果用户已登录返回 True，否则返回 False
        """
        return self.get_current_user() is not None
    
    def get_user_id(self) -> Optional[int]:
        """
        获取当前用户ID
        
        返回:
            用户ID，如未登录则返回 None
        """
        user = self.get_current_user()
        return user.get("id") if user else None
    
    def require_authentication(self, func):
        """
        要求用户认证的装饰器
        
        参数:
            func: 需要保护的路由函数
            
        返回:
            装饰后的函数
            
        说明:
            如果用户未登录，将重定向到首页并显示提示消息
        """
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                flash("请先登录", "warning")
                return redirect(url_for("index"))
            return func(*args, **kwargs)
        return decorated_function
    
    def require_role(self, required_role: str):
        """
        要求特定用户角色的装饰器
        
        参数:
            required_role: 所需的用户角色
            
        返回:
            装饰器函数
            
        说明:
            检查用户是否登录且具有所需角色，否则重定向
        """
        def decorator(func):
            @wraps(func)
            def decorated_function(*args, **kwargs):
                if not self.is_authenticated():
                    flash("请先登录", "warning")
                    return redirect(url_for("index"))
                
                user = self.get_current_user()
                if user.get("role") != required_role:
                    flash("权限不足", "error")
                    return redirect(url_for("home"))
                
                return func(*args, **kwargs)
            return decorated_function
        return decorator
    
    def safe_get_form_data(self, *fields) -> Dict[str, str]:
        """
        安全获取表单数据
        
        参数:
            *fields: 要提取的字段名列表
            
        返回:
            包含字段值的字典
            
        说明:
            自动去除字段值的首尾空白字符
        """
        data = {}
        for field in fields:
            data[field] = request.form.get(field, "").strip()
        return data
    
    def safe_get_args(self, *fields) -> Dict[str, str]:
        """
        安全获取URL参数
        
        参数:
            *fields: 要提取的参数名列表
            
        返回:
            包含参数值的字典
            
        说明:
            自动去除参数值的首尾空白字符
        """
        data = {}
        for field in fields:
            data[field] = request.args.get(field, "").strip()
        return data
    
    def validate_required_fields(self, data: Dict[str, str], *required_fields) -> bool:
        """
        验证必填字段
        
        参数:
            data: 要验证的数据字典
            *required_fields: 必填字段名列表
            
        返回:
            如果所有必填字段都存在且非空则返回 True，否则返回 False
        """
        for field in required_fields:
            if not data.get(field):
                return False
        return True
    
    def flash_error(self, message: str) -> None:
        """闪现错误消息"""
        flash(message, "error")
    
    def flash_success(self, message: str) -> None:
        """闪现成功消息"""
        flash(message, "success")
    
    def flash_warning(self, message: str) -> None:
        """闪现警告消息"""
        flash(message, "warning")
    
    def flash_info(self, message: str) -> None:
        """闪现提示消息"""
        flash(message, "info")
    
    def render_with_user_context(self, template: str, **kwargs) -> str:
        """
        使用用户上下文渲染模板
        
        参数:
            template: 模板文件名
            **kwargs: 额外的模板变量
            
        返回:
            渲染后的HTML字符串
            
        说明:
            自动添加当前用户信息和认证状态到模板上下文
        """
        context = {
            'current_user': self.get_current_user(),
            'is_authenticated': self.is_authenticated(),
            **kwargs
        }
        return render_template(template, **context)
    
    def login_user(self, user_data: UserData) -> None:
        """
        登录用户并设置会话数据
        
        参数:
            user_data: 要存储在会话中的用户数据
            
        说明:
            自动添加用户头像路径到用户数据中
        """
        user_data_with_photo = user_data.copy()
        user_data_with_photo["profile_photo"] = self.file_manager.get_profile_photo_path(user_data["id"])
        
        session["login_user"] = user_data_with_photo
    
    def logout_user(self) -> None:
        """注销当前用户，清除会话数据"""
        session.pop("login_user", None)
    
    def handle_database_error(self, error: Exception, user_message: str = "操作失败，请稍后重试") -> None:
        """
        Handle database errors gracefully
        
        Args:
            error: The exception that occurred
            user_message: User-friendly error message
        """
        print(f"Database error: {error}")  # Log the actual error
        self.flash_error(user_message)
    
    def redirect_to_referer(self, default_endpoint: str = 'home') -> Any:
        """
        Redirect to the referring page or default endpoint
        
        Args:
            default_endpoint: Default endpoint to redirect to
            
        Returns:
            Redirect response
        """
        referer = request.referrer
        if referer:
            return redirect(referer)
        return redirect(url_for(default_endpoint))
    
    def get_pagination_params(self, default_page: int = 1, default_per_page: int = 10) -> Dict[str, int]:
        """
        Get pagination parameters from request
        
        Args:
            default_page: Default page number
            default_per_page: Default items per page
            
        Returns:
            Dictionary with page and per_page values
        """
        try:
            page = int(request.args.get('page', default_page))
            per_page = int(request.args.get('per_page', default_per_page))
            
            # Validate values
            page = max(1, page)
            per_page = max(1, min(100, per_page))  # Limit to prevent abuse
            
            return {'page': page, 'per_page': per_page}
            
        except (ValueError, TypeError):
            return {'page': default_page, 'per_page': default_per_page} 