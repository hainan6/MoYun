"""
Base Handler Module
Provides base functionality for all request handlers
"""
from typing import Optional, Dict, Any, Union
from flask import session, request, flash, redirect, url_for, render_template
from functools import wraps

from core.data import DatabaseManager, UserData
from core.modules.file_manager import FileSystemManager


class HandlerError(Exception):
    """Custom exception for handler-related errors"""
    pass


class BaseHandler:
    """
    Base handler class providing common functionality for all route handlers
    """
    
    def __init__(self, database_manager: DatabaseManager, file_manager: FileSystemManager):
        """
        Initialize base handler
        
        Args:
            database_manager: Database manager instance
            file_manager: File manager instance
        """
        self.db = database_manager
        self.file_manager = file_manager
    
    def get_current_user(self) -> Optional[UserData]:
        """
        Get currently logged in user
        
        Returns:
            Current user data or None if not logged in
        """
        return session.get("login_user")
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated
        
        Returns:
            True if user is logged in, False otherwise
        """
        return self.get_current_user() is not None
    
    def get_user_id(self) -> Optional[int]:
        """
        Get current user ID
        
        Returns:
            User ID or None if not logged in
        """
        user = self.get_current_user()
        return user.get("id") if user else None
    
    def require_authentication(self, func):
        """
        Decorator to require authentication for a route
        
        Args:
            func: Route function to protect
            
        Returns:
            Decorated function
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
        Decorator to require specific user role
        
        Args:
            required_role: Required user role
            
        Returns:
            Decorator function
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
        Safely get form data
        
        Args:
            *fields: Field names to extract
            
        Returns:
            Dictionary of field values
        """
        data = {}
        for field in fields:
            data[field] = request.form.get(field, "").strip()
        return data
    
    def safe_get_args(self, *fields) -> Dict[str, str]:
        """
        Safely get URL arguments
        
        Args:
            *fields: Field names to extract
            
        Returns:
            Dictionary of argument values
        """
        data = {}
        for field in fields:
            data[field] = request.args.get(field, "").strip()
        return data
    
    def validate_required_fields(self, data: Dict[str, str], *required_fields) -> bool:
        """
        Validate that required fields are present and not empty
        
        Args:
            data: Data dictionary to validate
            *required_fields: Required field names
            
        Returns:
            True if all required fields are present, False otherwise
        """
        for field in required_fields:
            if not data.get(field):
                return False
        return True
    
    def flash_error(self, message: str) -> None:
        """Flash an error message"""
        flash(message, "error")
    
    def flash_success(self, message: str) -> None:
        """Flash a success message"""
        flash(message, "success")
    
    def flash_warning(self, message: str) -> None:
        """Flash a warning message"""
        flash(message, "warning")
    
    def flash_info(self, message: str) -> None:
        """Flash an info message"""
        flash(message, "info")
    
    def render_with_user_context(self, template: str, **kwargs) -> str:
        """
        Render template with user context
        
        Args:
            template: Template file name
            **kwargs: Additional template variables
            
        Returns:
            Rendered template
        """
        context = {
            'current_user': self.get_current_user(),
            'is_authenticated': self.is_authenticated(),
            **kwargs
        }
        return render_template(template, **context)
    
    def login_user(self, user_data: UserData) -> None:
        """
        Login user and set session data
        
        Args:
            user_data: User data to store in session
        """
        # Add profile photo path
        user_data_with_photo = user_data.copy()
        user_data_with_photo["profile_photo"] = self.file_manager.get_profile_photo_path(user_data["id"])
        
        session["login_user"] = user_data_with_photo
    
    def logout_user(self) -> None:
        """Logout current user"""
        if "login_user" in session:
            session.pop("login_user")
    
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