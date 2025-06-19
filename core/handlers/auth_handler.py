"""
用户认证处理器模块
================

本模块负责处理用户认证、注册和密码管理相关的所有功能。

主要功能:
    - 用户登录认证
    - 新用户注册
    - 密码重置
    - 验证码发送
    - 用户登出

依赖:
    - flask: Web框架
    - core.modules.network_services: 邮件服务
    - core.handlers.base_handler: 基础处理器
"""

import random
from typing import Any
from flask import Flask, request, redirect, url_for, session, Response

from core.modules.network_services import EmailService
from .base_handler import BaseHandler


class AuthenticationHandler(BaseHandler):
    """
    认证相关操作的处理器类
    
    主要职责:
        1. 处理用户登录请求
        2. 处理新用户注册
        3. 处理密码重置流程
        4. 发送验证码
        5. 处理用户登出
        
    继承:
        BaseHandler: 继承基础处理器的通用功能
    """
    
    def __init__(self, database_manager, file_manager, email_service: EmailService):
        """
        初始化认证处理器
        
        参数:
            database_manager: 数据库管理器实例
            file_manager: 文件管理器实例
            email_service: 邮件服务实例，用于发送验证码
        """
        super().__init__(database_manager, file_manager)
        self.email_service = email_service
    
    def register_routes(self, app: Flask) -> None:
        """
        注册认证相关的路由到Flask应用
        
        参数:
            app: Flask应用实例
            
        路由列表:
            - /: 首页，处理登录
            - /register: 用户注册
            - /sendCaptcha: 发送验证码
            - /resetPasswd: 密码重置
            - /logout: 用户登出
        """
        
        @app.route("/", methods=["GET", "POST"])
        def index() -> Any:
            """
            首页路由，处理登录请求
            
            返回:
                - GET: 渲染首页
                - POST: 处理登录，成功后重定向到主页
            """
            return self._handle_index()
        
        @app.route("/register", methods=["POST"])
        def register() -> Any:
            """
            用户注册路由
            
            返回:
                注册处理后的重定向响应
            """
            return self._handle_registration()
        
        @app.route("/sendCaptcha", methods=["POST"])
        def send_captcha() -> Any:
            """
            发送密码重置验证码路由
            
            返回:
                发送验证码后的重定向响应
            """
            return self._handle_send_captcha()
        
        @app.route("/resetPasswd", methods=["POST", "GET"])
        def reset_password() -> Any:
            """
            密码重置路由
            
            返回:
                密码重置处理后的重定向响应
            """
            return self._handle_password_reset()
        
        @app.route("/logout", methods=["GET"])
        def logout() -> Any:
            """
            用户登出路由
            
            返回:
                登出后重定向到首页
            """
            return self._handle_logout()
    
    def _handle_index(self) -> Any:
        """
        处理首页请求
        
        返回:
            - POST请求: 处理登录
            - GET请求: 显示首页
        """
        if request.method == "POST":
            return self._process_login()
        else:
            return self._show_index_page()
    
    def _process_login(self) -> Any:
        """
        处理登录表单提交
        
        处理流程:
            1. 获取并验证表单数据
            2. 验证登录凭据
            3. 获取用户信息
            4. 设置登录会话
            5. 更新用户登录时间
            
        返回:
            登录处理后的重定向响应
        """
        try:
            # 获取表单数据
            form_data = self.safe_get_form_data("account", "password")
            
            # 验证必填字段
            if not self.validate_required_fields(form_data, "account", "password"):
                self.flash_error("请输入用户名和密码")
                return redirect(url_for("index"))
            
            # 验证登录凭据
            user_id = self.db.verify_login(form_data["account"], form_data["password"])
            
            if user_id:
                # 登录成功
                user_data = self.db.get_user(id=user_id)
                if user_data:
                    self.login_user(user_data)
                    # 更新用户登录时间
                    self.db.update_user(user_id=user_id)
                    self.flash_success("登录成功")
                    return redirect(url_for("home"))
                else:
                    self.flash_error("用户信息获取失败")
                    return redirect(url_for("index"))
            else:
                # 登录失败
                self.flash_error("用户名或密码错误")
                return redirect(url_for("index"))
                
        except Exception as e:
            self.handle_database_error(e, "登录失败，请稍后重试")
            return redirect(url_for("index"))
    
    def _show_index_page(self) -> Any:
        """
        显示首页
        
        说明:
            如果用户已登录，重定向到主页
            否则显示登录页面
        
        返回:
            页面响应或重定向
        """
        if self.is_authenticated():
            # 已登录，重定向到主页
            return redirect(url_for("home"))
        
        return self.render_with_user_context("index.html")
    
    def _handle_registration(self) -> Any:
        """
        处理用户注册
        
        处理流程:
            1. 获取并验证注册表单数据
            2. 检查用户是否已存在
            3. 创建新用户
            
        返回:
            注册处理后的重定向响应
        """
        try:
            # 获取表单数据
            form_data = self.safe_get_form_data("account", "password", "email", "telephone")
            
            # 验证必填字段
            if not self.validate_required_fields(form_data, "account", "password", "email"):
                self.flash_warning("账号、密码、邮箱是必须的")
                return redirect(url_for("index") + "#register")
            
            # 检查用户是否已存在
            existing_user = self.db.get_user(account=form_data["account"])
            if existing_user:
                self.flash_info("用户名已存在，请尝试登录或找回密码")
                return redirect(url_for("index") + "#login")
            
            # 创建新用户
            user_id = self.db.create_user(
                account=form_data["account"],
                raw_password=form_data["password"],
                email=form_data["email"],
                telephone=form_data["telephone"]
            )
            
            if user_id:
                self.flash_success("注册成功，请登录")
                return redirect(url_for("index") + "#login")
            else:
                self.flash_error("注册失败，请稍后重试")
                return redirect(url_for("index") + "#register")
                
        except Exception as e:
            self.handle_database_error(e, "注册失败，请稍后重试")
            return redirect(url_for("index") + "#register")
    
    def _handle_send_captcha(self) -> Any:
        """
        处理发送验证码请求
        
        处理流程:
            1. 验证用户名
            2. 检查用户是否存在
            3. 检查用户邮箱
            4. 生成并发送验证码
            
        返回:
            发送验证码后的重定向响应
        """
        try:
            # 获取表单数据
            form_data = self.safe_get_form_data("account")
            
            if not form_data["account"]:
                self.flash_warning("请输入用户名")
                return redirect(url_for("index") + "#resetPasswd")
            
            # 检查用户是否存在
            user = self.db.get_user(account=form_data["account"])
            if not user:
                self.flash_info("用户名不存在，请先注册")
                return redirect(url_for("index") + "#register")
            
            if not user.get("email"):
                self.flash_error("该用户未绑定邮箱，无法重置密码")
                return redirect(url_for("index") + "#resetPasswd")
            
            # 生成验证码
            captcha = str(random.randint(100000, 999999))
            
            # 发送验证码
            email_sent = self.email_service.send_verification_code(user["email"], captcha)
            
            if email_sent:
                # Store verification code and account in session
                session["captcha"] = captcha
                session["resetPasswdAccount"] = form_data["account"]
                self.flash_success("验证码已发送，请注意查收")
            else:
                self.flash_error("验证码发送失败，请稍后重试")
            
            return redirect(url_for("index") + "#resetPasswd")
            
        except Exception as e:
            self.handle_database_error(e, "验证码发送失败")
            return redirect(url_for("index") + "#resetPasswd")
    
    def _handle_password_reset(self) -> Any:
        """Handle password reset"""
        if request.method != "POST":
            return redirect(url_for("index") + "#resetPasswd")
        
        try:
            # Get form data
            form_data = self.safe_get_form_data("captcha", "password")
            
            # Validate required fields
            if not self.validate_required_fields(form_data, "captcha", "password"):
                self.flash_warning("请输入验证码和新密码")
                return redirect(url_for("index") + "#resetPasswd")
            
            # Get stored verification data from session
            stored_captcha = session.get("captcha")
            account = session.get("resetPasswdAccount")
            
            if not stored_captcha or not account:
                self.flash_error("验证码已过期，请重新获取")
                return redirect(url_for("index") + "#resetPasswd")
            
            # Verify captcha
            if form_data["captcha"] != stored_captcha:
                self.flash_warning("验证码错误")
                return redirect(url_for("index") + "#resetPasswd")
            
            # Update password
            success = self.db.update_user(account=account, password=form_data["password"])
            
            if success:
                # Clear session data
                session.pop("captcha", None)
                session.pop("resetPasswdAccount", None)
                
                self.flash_success("密码修改成功，请重新登录")
                return redirect(url_for("index") + "#login")
            else:
                self.flash_error("密码修改失败，请稍后重试")
                return redirect(url_for("index") + "#resetPasswd")
                
        except Exception as e:
            self.handle_database_error(e, "密码重置失败")
            return redirect(url_for("index") + "#resetPasswd")
    
    def _handle_logout(self) -> Response:
        """Handle user logout"""
        if self.is_authenticated():
            self.logout_user()
            response = redirect(url_for("index"))
            response.delete_cookie('session')
            self.flash_success("您已成功退出账号")
            return response
        else:
            return redirect(url_for("index")) 