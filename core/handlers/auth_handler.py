"""
Authentication Handler Module
Handles user authentication, registration, and password management
"""
import random
from typing import Any
from flask import Flask, request, redirect, url_for, session, Response

from core.modules.network_services import EmailService
from .base_handler import BaseHandler


class AuthenticationHandler(BaseHandler):
    """
    Handler for authentication-related operations
    """
    
    def __init__(self, database_manager, file_manager, email_service: EmailService):
        """
        Initialize authentication handler
        
        Args:
            database_manager: Database manager instance
            file_manager: File manager instance
            email_service: Email service instance
        """
        super().__init__(database_manager, file_manager)
        self.email_service = email_service
    
    def register_routes(self, app: Flask) -> None:
        """
        Register authentication routes with Flask app
        
        Args:
            app: Flask application instance
        """
        
        @app.route("/", methods=["GET", "POST"])
        def index() -> Any:
            """
            Main index page handling login
            
            Returns:
                Response for index page or redirect
            """
            return self._handle_index()
        
        @app.route("/register", methods=["POST"])
        def register() -> Any:
            """
            User registration endpoint
            
            Returns:
                Redirect response after registration attempt
            """
            return self._handle_registration()
        
        @app.route("/sendCaptcha", methods=["POST"])
        def send_captcha() -> Any:
            """
            Send verification code for password reset
            
            Returns:
                Redirect response after sending captcha
            """
            return self._handle_send_captcha()
        
        @app.route("/resetPasswd", methods=["POST", "GET"])
        def reset_password() -> Any:
            """
            Password reset endpoint
            
            Returns:
                Redirect response after password reset attempt
            """
            return self._handle_password_reset()
        
        @app.route("/logout", methods=["GET"])
        def logout() -> Any:
            """
            User logout endpoint
            
            Returns:
                Redirect response after logout
            """
            return self._handle_logout()
    
    def _handle_index(self) -> Any:
        """Handle index page requests"""
        if request.method == "POST":
            return self._process_login()
        else:
            return self._show_index_page()
    
    def _process_login(self) -> Any:
        """Process login form submission"""
        try:
            # Get form data
            form_data = self.safe_get_form_data("account", "password")
            
            # Validate required fields
            if not self.validate_required_fields(form_data, "account", "password"):
                self.flash_error("请输入用户名和密码")
                return redirect(url_for("index"))
            
            # Verify login credentials
            user_id = self.db.verify_login(form_data["account"], form_data["password"])
            
            if user_id:
                # Login successful
                user_data = self.db.get_user(id=user_id)
                if user_data:
                    self.login_user(user_data)
                    # Update user login time
                    self.db.update_user(user_id=user_id)
                    self.flash_success("登录成功")
                    return redirect(url_for("home"))
                else:
                    self.flash_error("用户信息获取失败")
                    return redirect(url_for("index"))
            else:
                # Login failed
                self.flash_error("用户名或密码错误")
                return redirect(url_for("index"))
                
        except Exception as e:
            self.handle_database_error(e, "登录失败，请稍后重试")
            return redirect(url_for("index"))
    
    def _show_index_page(self) -> Any:
        """Show index page"""
        if self.is_authenticated():
            # Already logged in, redirect to home
            return redirect(url_for("home"))
        
        return self.render_with_user_context("index.html")
    
    def _handle_registration(self) -> Any:
        """Handle user registration"""
        try:
            # Get form data
            form_data = self.safe_get_form_data("account", "password", "email", "telephone")
            
            # Validate required fields
            if not self.validate_required_fields(form_data, "account", "password", "email"):
                self.flash_warning("账号、密码、邮箱是必须的")
                return redirect(url_for("index") + "#register")
            
            # Check if user already exists
            existing_user = self.db.get_user(account=form_data["account"])
            if existing_user:
                self.flash_info("用户名已存在，请尝试登录或找回密码")
                return redirect(url_for("index") + "#login")
            
            # Create new user
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
        """Handle sending verification code"""
        try:
            # Get form data
            form_data = self.safe_get_form_data("account")
            
            if not form_data["account"]:
                self.flash_warning("请输入用户名")
                return redirect(url_for("index") + "#resetPasswd")
            
            # Check if user exists
            user = self.db.get_user(account=form_data["account"])
            if not user:
                self.flash_info("用户名不存在，请先注册")
                return redirect(url_for("index") + "#register")
            
            if not user.get("email"):
                self.flash_error("该用户未绑定邮箱，无法重置密码")
                return redirect(url_for("index") + "#resetPasswd")
            
            # Generate verification code
            captcha = str(random.randint(100000, 999999))
            
            # Send verification code
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