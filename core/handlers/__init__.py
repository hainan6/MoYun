"""
Handlers Package
Contains all request handlers for the application
"""

from .base_handler import BaseHandler
from .auth_handler import AuthenticationHandler

# Compatibility imports for old service layer
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
    print(f"Warning: Old service imports failed: {e}")


def register_authentication_routes(app, file_manager, database_manager, email_service):
    """Register authentication routes using new handler"""
    auth_handler = AuthenticationHandler(database_manager, file_manager, email_service)
    auth_handler.register_routes(app)


def register_book_routes(app, file_manager, database_manager):
    """Register book routes (compatibility wrapper)"""
    try:
        bookResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"Warning: Book routes registration failed: {e}")


def register_chat_routes(app, file_manager, database_manager):
    """Register chat routes (compatibility wrapper)"""
    try:
        chatResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"Warning: Chat routes registration failed: {e}")


def register_homepage_routes(app, file_manager, database_manager, api_service):
    """Register homepage routes (compatibility wrapper)"""
    try:
        homepageResponse(app, file_manager, database_manager, api_service)
    except Exception as e:
        print(f"Warning: Homepage routes registration failed: {e}")


def register_error_routes(app, file_manager, database_manager):
    """Register error routes (compatibility wrapper)"""
    try:
        errorResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"Warning: Error routes registration failed: {e}")


def register_journal_routes(app, file_manager, database_manager):
    """Register journal routes (compatibility wrapper)"""
    try:
        journalResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"Warning: Journal routes registration failed: {e}")


def register_ai_routes(app, api_service):
    """Register AI routes (compatibility wrapper)"""
    try:
        lLMResponse(app, api_service)
    except Exception as e:
        print(f"Warning: AI routes registration failed: {e}")


def register_profile_routes(app, file_manager, database_manager):
    """Register profile routes (compatibility wrapper)"""
    try:
        profileResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"Warning: Profile routes registration failed: {e}")


def register_group_routes(app, file_manager, database_manager):
    """Register group routes (compatibility wrapper)"""
    try:
        groupResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"Warning: Group routes registration failed: {e}")


def register_search_routes(app, file_manager, database_manager):
    """Register search routes (compatibility wrapper)"""
    try:
        searchResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"Warning: Search routes registration failed: {e}")


def register_message_routes(app, file_manager, database_manager):
    """Register message routes (compatibility wrapper)"""
    try:
        messageResponse(app, file_manager, database_manager)
    except Exception as e:
        print(f"Warning: Message routes registration failed: {e}")


def configure_security_middleware(app):
    """Configure security middleware (compatibility wrapper)"""
    try:
        securityCheck(app)
    except Exception as e:
        print(f"Warning: Security middleware configuration failed: {e}")


__all__ = [
    'BaseHandler',
    'AuthenticationHandler',
    'register_authentication_routes',
    'register_book_routes', 
    'register_chat_routes',
    'register_homepage_routes',
    'register_error_routes',
    'register_journal_routes',
    'register_ai_routes',
    'register_profile_routes',
    'register_group_routes',
    'register_search_routes',
    'register_message_routes',
    'configure_security_middleware'
] 