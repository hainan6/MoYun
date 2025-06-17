"""
Data Package
Contains all data layer components including models, database management, and caching
"""

from .models import database, User, Book, Journal, JournalComment, JournalLike, Group, GroupDiscussion, GroupDiscussionReply, GroupUser, Chat, Error
from .database_manager import DatabaseManager
from .cache_manager import RedisCacheManager
from .utilities import (
    UserData, BookData, JournalData, JournalCommentData, JournalLikeData,
    GroupData, GroupDiscussionData, GroupDiscussionReplyData, GroupUserData, 
    ChatData, ErrorData, UnreadMessagesData,
    extract_user_data, extract_book_data, extract_journal_data,
    extract_journal_comment_data, extract_journal_like_data,
    extract_group_data, extract_group_discussion_data,
    extract_group_discussion_reply_data, extract_group_user_data,
    extract_chat_data, extract_error_data
)

__all__ = [
    # Database and cache
    'database',
    'DatabaseManager',
    'RedisCacheManager',
    
    # Models
    'User',
    'Book', 
    'Journal',
    'JournalComment',
    'JournalLike',
    'Group',
    'GroupDiscussion',
    'GroupDiscussionReply',
    'GroupUser',
    'Chat',
    'Error',
    
    # Data types
    'UserData',
    'BookData',
    'JournalData',
    'JournalCommentData',
    'JournalLikeData',
    'GroupData',
    'GroupDiscussionData',
    'GroupDiscussionReplyData',
    'GroupUserData',
    'ChatData',
    'ErrorData',
    'UnreadMessagesData',
    
    # Utility functions
    'extract_user_data',
    'extract_book_data',
    'extract_journal_data',
    'extract_journal_comment_data',
    'extract_journal_like_data',
    'extract_group_data',
    'extract_group_discussion_data',
    'extract_group_discussion_reply_data',
    'extract_group_user_data',
    'extract_chat_data',
    'extract_error_data'
] 