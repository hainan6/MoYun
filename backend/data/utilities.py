"""
Data Utilities Module
Provides TypedDict definitions and utility functions for data extraction and conversion
"""
from typing import TypedDict, List, Union, Optional
from datetime import datetime

# Type definitions for data transfer objects


class UserData(TypedDict):
    """User data structure for API responses"""
    id: int
    account: str
    password: Optional[str]
    signature: str
    email: str
    telephone: str
    role: str


class BookData(TypedDict):
    """Book data structure for API responses"""
    id: int
    isbn: str
    title: str
    origin_title: str
    subtitle: str
    author: str
    page: Union[int, str]
    publish_date: str
    publisher: str
    description: str
    douban_score: Union[float, str]
    douban_id: str
    bangumi_score: Union[float, str]
    bangumi_id: str
    category: str


class JournalData(TypedDict):
    """Journal data structure for API responses"""
    id: int
    title: str
    first_paragraph: str
    content: List[str]
    publish_time: str
    author_id: int
    book_id: int
    like_num: Optional[int]
    comment_num: Optional[int]


class JournalCommentData(TypedDict):
    """Journal comment data structure for API responses"""
    id: int
    publish_time: str
    author_id: int
    journal_id: int
    content: str
    is_read: bool


class JournalLikeData(TypedDict):
    """Journal like data structure for API responses"""
    author_id: int
    journal_id: int
    publish_time: str


class GroupData(TypedDict):
    """Group data structure for API responses"""
    id: int
    name: str
    founder_id: int
    establish_time: str
    description: str


class GroupDiscussionData(TypedDict):
    """Group discussion data structure for API responses"""
    id: int
    poster_id: int
    group_id: int
    post_time: str
    title: str
    content: str
    is_read: bool


class GroupDiscussionReplyData(TypedDict):
    """Group discussion reply data structure for API responses"""
    author_id: int
    discussion_id: int
    reply_time: str
    content: str
    is_read: bool


class GroupUserData(TypedDict):
    """Group user data structure for API responses"""
    user_id: int
    group_id: int
    join_time: str


class ChatData(TypedDict):
    """Chat data structure for API responses"""
    id: int
    sender_id: int
    receiver_id: int
    content: str
    send_time: str
    is_read: bool


class ErrorData(TypedDict):
    """Error data structure for API responses"""
    error_code: int
    title: str
    title_en: str
    content: str
    publish_time: str
    reference_link: str


class UnreadMessagesData(TypedDict):
    """Unread messages data structure for API responses"""
    journal_comments: List[JournalCommentData]
    group_discussions: List[GroupDiscussionData]
    discussion_replies: List[GroupDiscussionReplyData]
    chats: List[ChatData]


# Utility functions for data extraction

def extract_user_data(user_model, include_password: bool = False) -> UserData:
    """
    Extract user data from User model instance
    
    Args:
        user_model: User model instance
        include_password: Whether to include password in result
        
    Returns:
        UserData dictionary
    """
    return UserData(
        id=user_model.id,
        account=user_model.account,
        password=user_model.password if include_password else None,
        signature=user_model.signature or "",
        email=user_model.email or "",
        telephone=user_model.telephone or "",
        role=user_model.role.value if hasattr(user_model.role, 'value') else user_model.role
    )


def extract_book_data(book_model) -> BookData:
    """
    Extract book data from Book model instance
    
    Args:
        book_model: Book model instance
        
    Returns:
        BookData dictionary
    """
    return BookData(
        id=book_model.id,
        isbn=book_model.isbn or "",
        title=book_model.title,
        origin_title=book_model.origin_title or "",
        subtitle=book_model.subtitle or "",
        author=book_model.author,
        page=book_model.page if book_model.page else "",
        publish_date=book_model.publish_date.strftime("%Y-%m-%d") if book_model.publish_date else "",
        publisher=book_model.publisher or "",
        description=book_model.description or "",
        douban_score=book_model.douban_score if book_model.douban_score else "",
        douban_id=book_model.douban_id or "",
        bangumi_score=book_model.bangumi_score if book_model.bangumi_score else "",
        bangumi_id=book_model.bangumi_id or "",
        category=book_model.category.value if hasattr(book_model.category, 'value') else (book_model.category or "")
    )


def extract_journal_data(journal_model, comment_count: int = 0, like_count: int = 0) -> JournalData:
    """
    Extract journal data from Journal model instance
    
    Args:
        journal_model: Journal model instance
        comment_count: Number of comments
        like_count: Number of likes
        
    Returns:
        JournalData dictionary
    """
    return JournalData(
        id=journal_model.id,
        title=journal_model.title,
        first_paragraph=journal_model.first_paragraph,
        content=journal_model.content.split("\n") if isinstance(journal_model.content, str) else journal_model.content,
        publish_time=journal_model.publish_time.strftime("%Y-%m-%d %H:%M:%S") if journal_model.publish_time else "",
        author_id=journal_model.author_id,
        book_id=journal_model.book_id,
        like_num=like_count,
        comment_num=comment_count
    )


def extract_journal_comment_data(comment_model) -> JournalCommentData:
    """
    Extract journal comment data from JournalComment model instance
    
    Args:
        comment_model: JournalComment model instance
        
    Returns:
        JournalCommentData dictionary
    """
    return JournalCommentData(
        id=comment_model.id,
        publish_time=comment_model.publish_time.strftime("%Y-%m-%d %H:%M:%S") if comment_model.publish_time else "",
        author_id=comment_model.author_id,
        journal_id=comment_model.journal_id,
        content=comment_model.content,
        is_read=comment_model.is_read
    )


def extract_journal_like_data(like_model) -> JournalLikeData:
    """
    Extract journal like data from JournalLike model instance
    
    Args:
        like_model: JournalLike model instance
        
    Returns:
        JournalLikeData dictionary
    """
    return JournalLikeData(
        author_id=like_model.author_id,
        journal_id=like_model.journal_id,
        publish_time=like_model.publish_time.strftime("%Y-%m-%d %H:%M:%S") if like_model.publish_time else ""
    )


def extract_group_data(group_model) -> GroupData:
    """
    Extract group data from Group model instance
    
    Args:
        group_model: Group model instance
        
    Returns:
        GroupData dictionary
    """
    return GroupData(
        id=group_model.id,
        name=group_model.name,
        founder_id=group_model.founder_id,
        establish_time=group_model.establish_time.strftime("%Y-%m-%d %H:%M:%S") if group_model.establish_time else "",
        description=group_model.description or ""
    )


def extract_group_discussion_data(discussion_model) -> GroupDiscussionData:
    """
    Extract group discussion data from GroupDiscussion model instance
    
    Args:
        discussion_model: GroupDiscussion model instance
        
    Returns:
        GroupDiscussionData dictionary
    """
    return GroupDiscussionData(
        id=discussion_model.id,
        poster_id=discussion_model.poster_id,
        group_id=discussion_model.group_id,
        post_time=discussion_model.post_time.strftime("%Y-%m-%d %H:%M:%S") if discussion_model.post_time else "",
        title=discussion_model.title,
        content=discussion_model.content,
        is_read=discussion_model.is_read
    )


def extract_group_discussion_reply_data(reply_model) -> GroupDiscussionReplyData:
    """
    Extract group discussion reply data from GroupDiscussionReply model instance
    
    Args:
        reply_model: GroupDiscussionReply model instance
        
    Returns:
        GroupDiscussionReplyData dictionary
    """
    return GroupDiscussionReplyData(
        author_id=reply_model.author_id,
        discussion_id=reply_model.discussion_id,
        reply_time=reply_model.reply_time.strftime("%Y-%m-%d %H:%M:%S") if reply_model.reply_time else "",
        content=reply_model.content,
        is_read=reply_model.is_read
    )


def extract_group_user_data(group_user_model) -> GroupUserData:
    """
    Extract group user data from GroupUser model instance
    
    Args:
        group_user_model: GroupUser model instance
        
    Returns:
        GroupUserData dictionary
    """
    return GroupUserData(
        user_id=group_user_model.user_id,
        group_id=group_user_model.group_id,
        join_time=group_user_model.join_time.strftime("%Y-%m-%d %H:%M:%S") if group_user_model.join_time else ""
    )


def extract_chat_data(chat_model) -> ChatData:
    """
    Extract chat data from Chat model instance
    
    Args:
        chat_model: Chat model instance
        
    Returns:
        ChatData dictionary
    """
    return ChatData(
        id=chat_model.id,
        sender_id=chat_model.sender_id,
        receiver_id=chat_model.receiver_id,
        content=chat_model.content,
        send_time=chat_model.send_time.strftime("%Y-%m-%d %H:%M:%S") if chat_model.send_time else "",
        is_read=chat_model.is_read
    )


def extract_error_data(error_model) -> ErrorData:
    """
    Extract error data from Error model instance
    
    Args:
        error_model: Error model instance
        
    Returns:
        ErrorData dictionary
    """
    return ErrorData(
        error_code=error_model.error_code,
        title=error_model.title,
        title_en=error_model.title_en or "",
        content=error_model.content or "",
        publish_time=error_model.publish_time.strftime("%Y-%m-%d %H:%M:%S") if error_model.publish_time else "",
        reference_link=error_model.reference_link or ""
    )


def format_datetime_string(dt: Union[str, datetime]) -> str:
    """
    Format datetime to string
    
    Args:
        dt: Datetime object or string
        
    Returns:
        Formatted datetime string
    """
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt if dt else ""


def parse_datetime_string(dt_str: str) -> Optional[datetime]:
    """
    Parse datetime string to datetime object
    
    Args:
        dt_str: Datetime string
        
    Returns:
        Datetime object or None
    """
    if not dt_str:
        return None
    
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d")
        except ValueError:
            return None


def safe_int_conversion(value: Union[str, int, None]) -> Optional[int]:
    """
    Safely convert value to integer
    
    Args:
        value: Value to convert
        
    Returns:
        Integer value or None
    """
    if value is None or value == "":
        return None
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_float_conversion(value: Union[str, float, None]) -> Optional[float]:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        
    Returns:
        Float value or None
    """
    if value is None or value == "":
        return None
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None 