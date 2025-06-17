"""
Main Application Entry Point
Refactored MoYun Reading Platform Application
"""
import os
from flask import Flask

# Import refactored core modules
from core import (
    config_manager,
    FileSystemManager, 
    EmailService,
    ExternalAPIService
)

# Import data layer (to be refactored next)
from core.data.database_manager import DatabaseManager

# Import handlers (to be refactored next) 
from core.handlers import (
    register_authentication_routes,
    register_book_routes,
    register_chat_routes,
    register_homepage_routes,
    register_error_routes,
    register_journal_routes,
    register_ai_routes,
    register_profile_routes,
    register_group_routes,
    register_search_routes,
    register_message_routes,
    configure_security_middleware
)


class MoYunApplication:
    """
    Main application class for MoYun Reading Platform
    """
    
    def __init__(self):
        """Initialize the application"""
        self.app = self._create_flask_app()
        self._initialize_services()
        self._register_routes()
        self._configure_security()
    
    def _create_flask_app(self) -> Flask:
        """Create and configure Flask application"""
        app = Flask(
            __name__,
            template_folder=(os.getcwd() + "/templates").replace("\\", "/"),
            static_folder=(os.getcwd() + "/static").replace("\\", "/")
        )
        
        # Load Flask configuration from config manager
        app.config.update(config_manager.get_flask_config())
        
        return app
    
    def _initialize_services(self) -> None:
        """Initialize core services"""
        # Initialize services
        self.email_service = EmailService()
        self.api_service = ExternalAPIService()
        self.file_manager = FileSystemManager()
        self.database_manager = DatabaseManager(self.app)
    
    def _register_routes(self) -> None:
        """Register all application routes"""
        # Register route handlers with services
        register_authentication_routes(
            self.app, 
            self.file_manager, 
            self.database_manager, 
            self.email_service
        )
        
        register_book_routes(
            self.app,
            self.file_manager,
            self.database_manager
        )
        
        register_chat_routes(
            self.app,
            self.file_manager,
            self.database_manager
        )
        
        register_homepage_routes(
            self.app,
            self.file_manager,
            self.database_manager,
            self.api_service
        )
        
        register_error_routes(
            self.app,
            self.file_manager,
            self.database_manager
        )
        
        register_journal_routes(
            self.app,
            self.file_manager,
            self.database_manager
        )
        
        register_ai_routes(
            self.app,
            self.api_service
        )
        
        register_profile_routes(
            self.app,
            self.file_manager,
            self.database_manager
        )
        
        register_group_routes(
            self.app,
            self.file_manager,
            self.database_manager
        )
        
        register_search_routes(
            self.app,
            self.file_manager,
            self.database_manager
        )
        
        register_message_routes(
            self.app,
            self.file_manager,
            self.database_manager
        )
    
    def _configure_security(self) -> None:
        """Configure security middleware"""
        configure_security_middleware(self.app)
    
    def run(self, debug: bool = True, host: str = "0.0.0.0") -> None:
        """Run the application"""
        port = config_manager.get_config("Flask", "Port")
        self.app.run(
            port=port,
            debug=debug,
            host=host
        )
    
    def get_flask_app(self) -> Flask:
        """Get the Flask application instance"""
        return self.app


def create_application() -> MoYunApplication:
    """
    Application factory function
    
    Returns:
        Configured MoYunApplication instance
    """
    return MoYunApplication()


# For direct execution
if __name__ == "__main__":
    app_instance = create_application()
    app_instance.run(debug=True) 