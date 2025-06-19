"""
Database Manager Module
Handles all database operations with modern architecture and caching
"""
from datetime import datetime
from typing import Union, List, Optional, Literal, Dict, Any
from flask import Flask
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from core.config.settings import config_manager
from .models import database, User, Book, Journal, JournalComment, JournalLike, Group, GroupDiscussion, GroupDiscussionReply, GroupUser, Chat, Error
from .cache_manager import RedisCacheManager
from .utilities import (
    UserData, BookData, JournalData, JournalCommentData, JournalLikeData,
    GroupData, GroupDiscussionData, GroupDiscussionReplyData, GroupUserData, ChatData, ErrorData,
    extract_user_data, extract_book_data, extract_journal_data, extract_journal_comment_data,
    extract_journal_like_data, extract_group_data, extract_group_discussion_data,
    extract_group_discussion_reply_data, extract_group_user_data, extract_chat_data, extract_error_data
)


class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass


class DatabaseManager:
    """
    Modern database manager with caching and improved error handling
    """
    
    def __init__(self, app: Flask):
        """Initialize database manager with Flask app"""
        try:
            # Setup database configuration
            db_config = config_manager.get_database_config()
            client = f"{db_config['Type'].lower()}+{db_config['Driver']}"
            host = db_config["Host"]
            port = db_config["Port"]
            account = db_config["Account"]
            password = db_config["Password"]
            database_name = db_config["Database"]
            
            uri = f"{client}://{account}:{password}@{host}:{port}/{database_name}"
            app.config["SQLALCHEMY_DATABASE_URI"] = uri
            app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
            
            database.init_app(app)
            
            # Initialize cache manager
            self.cache = RedisCacheManager()
            
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    # User operations
    
    def create_user(self, account: str, raw_password: str, email: str, telephone: str, role: str = "student") -> int:
        """
        Create a new user
        
        Args:
            account: Username
            raw_password: Plain text password
            email: Email address
            telephone: Phone number
            role: User role
            
        Returns:
            User ID
            
        Raises:
            DatabaseError: If user creation fails
        """
        try:
            user = User(
                account=account,
                password=generate_password_hash(raw_password),
                signature="",
                email=email if email else None,
                telephone=telephone if telephone else None,
                role=role
            )
            
            database.session.add(user)
            database.session.commit()
            
            return user.id
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to create user: {e}")
    
    def get_user(self, limit: int = 1, include_password: bool = False, **filters) -> Union[List[UserData], UserData, None]:
        """
        Get user information
        
        Args:
            limit: Number of users to return (1 for single user, 0 for all)
            include_password: Whether to include password in result
            **filters: Filter criteria including User fields and 'keyword' for fuzzy search
            
        Returns:
            User data or list of user data
        """
        try:
            # Check cache for single user by ID
            if "id" in filters and limit == 1:
                cached_user = self.cache.get_cache(f"User_{filters['id']}")
                if cached_user:
                    # Parse cached data and return as UserData
                    pass  # Simplified for now
            
            # Build query
            if filters and "keyword" in filters:
                query = User.query.filter(User.account.like(f"%{filters.get('keyword')}%"))
            else:
                filter_dict = {k: v for k, v in filters.items() if k != 'keyword'}
                query = User.query.filter_by(**filter_dict) if filter_dict else User.query
            
            # Execute query
            if limit == 1:
                user = query.first()
                if user:
                    user_data = extract_user_data(user, include_password)
                    # Cache the result
                    self.cache.set_cache(f"User_{user_data['id']}", str(user_data), 1200)
                    return user_data
                return None
                
            elif limit > 1:
                users = query.limit(limit).all()
                return [extract_user_data(user, include_password) for user in users]
                
            else:
                users = query.all()
                return [extract_user_data(user, include_password) for user in users]
                
        except Exception as e:
            raise DatabaseError(f"Failed to get user: {e}")
    
    def update_user(self, user_id: Optional[int] = None, account: Optional[str] = None, **kwargs) -> bool:
        """
        Update user information
        
        Args:
            user_id: User ID to identify user
            account: Account name to identify user
            **kwargs: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_id:
                user = User.query.filter_by(id=user_id).first()
            elif account:
                user = User.query.filter_by(account=account).first()
            else:
                return False
            
            if not user:
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(user, key):
                    if key == "password":
                        setattr(user, key, generate_password_hash(value))
                    else:
                        setattr(user, key, value)
            
            database.session.commit()
            
            # Clear cache
            self.cache.delete_cache(f"User_{user.id}")
            
            return True
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to update user: {e}")
    
    def verify_login(self, account: str, password: str) -> Union[int, bool]:
        """
        Verify login credentials
        
        Args:
            account: Username
            password: Plain text password
            
        Returns:
            User ID if successful, False if failed
        """
        try:
            users = self.get_user(limit=0, include_password=True, account=account)
            
            if not users:
                return False
            
            for user in users:
                if check_password_hash(user["password"], password):
                    return user["id"]
            
            return False
            
        except Exception as e:
            raise DatabaseError(f"Login verification failed: {e}")
    
    # Journal operations
    
    def create_journal(self, title: str, content: Union[List, str], publish_time: str, 
                      author_id: int, book_id: int) -> int:
        """
        Create a new journal entry
        
        Args:
            title: Journal title
            content: Journal content
            publish_time: Publishing time
            author_id: Author user ID
            book_id: Related book ID
            
        Returns:
            Journal ID
        """
        try:
            if isinstance(content, list):
                content_str = "\n".join(content)
                first_paragraph = content[0]
            else:
                content_str = content
                first_paragraph = content.split("\n")[0]
            
            journal = Journal(
                title=title,
                first_paragraph=first_paragraph,
                content=content_str,
                publish_time=publish_time,
                author_id=author_id,
                book_id=book_id
            )
            
            database.session.add(journal)
            database.session.commit()
            
            return journal.id
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to create journal: {e}")
    
    def get_journal(self, limit: int = 1, **filters) -> Union[List[JournalData], JournalData, None]:
        """
        Get journal information
        
        Args:
            limit: Number of journals to return
            **filters: Filter criteria
            
        Returns:
            Journal data or list of journal data
        """
        try:
            # Build query
            if filters and "keyword" in filters:
                # Get related book for keyword search
                keyword = filters.get('keyword')
                related_book = self.get_book(keyword=keyword)
                
                if related_book:
                    query = Journal.query.filter(
                        Journal.title.like(f"%{keyword}%") |
                        Journal.content.like(f"%{keyword}%") |
                        (Journal.book_id == related_book['id'])
                    )
                else:
                    query = Journal.query.filter(
                        Journal.title.like(f"%{keyword}%") |
                        Journal.content.like(f"%{keyword}%")
                    )
            else:
                filter_dict = {k: v for k, v in filters.items() if k != 'keyword'}
                query = Journal.query.filter_by(**filter_dict) if filter_dict else Journal.query
            
            # Execute query
            if limit == 1:
                journal = query.first()
                if journal:
                    comment_count = self.get_journal_comment_count(journal_id=journal.id)
                    like_count = self.get_journal_like_count(journal.id)
                    return extract_journal_data(journal, comment_count, like_count)
                return None
                
            elif limit > 1:
                journals = query.limit(limit).all()
                result = []
                for journal in journals:
                    comment_count = self.get_journal_comment_count(journal_id=journal.id)
                    like_count = self.get_journal_like_count(journal.id)
                    result.append(extract_journal_data(journal, comment_count, like_count))
                return result
                
            else:
                journals = query.all()
                result = []
                for journal in journals:
                    comment_count = JournalComment.query.filter_by(journal_id=journal.id).count()
                    like_count = JournalLike.query.filter_by(journal_id=journal.id).count()
                    result.append(extract_journal_data(journal, comment_count, like_count))
                return result
                
        except Exception as e:
            raise DatabaseError(f"Failed to get journal: {e}")
    
    # Journal comment operations
    
    def create_journal_comment(self, journal_id: int, content: Union[str, List], 
                              author_id: int, publish_time: Optional[str] = None) -> int:
        """Create a journal comment"""
        try:
            if not publish_time:
                publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            comment = JournalComment(
                publish_time=publish_time,
                author_id=author_id,
                journal_id=journal_id,
                content=content
            )
            
            # Auto-mark as read if author is the journal author
            journal = Journal.query.filter_by(id=journal_id).first()
            if journal and author_id == journal.author_id:
                comment.is_read = True
            
            database.session.add(comment)
            database.session.commit()
            
            return comment.id
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to create journal comment: {e}")
    
    def get_journal_comments(self, **filters) -> List[JournalCommentData]:
        """Get journal comments"""
        try:
            comments = JournalComment.query.filter_by(**filters).order_by(JournalComment.publish_time.asc()).all()
            return [extract_journal_comment_data(comment) for comment in comments]
        except Exception as e:
            raise DatabaseError(f"Failed to get journal comments: {e}")
    
    def get_journal_comment_count(self, **filters) -> int:
        """Get journal comment count"""
        try:
            return JournalComment.query.filter_by(**filters).count()
        except Exception as e:
            raise DatabaseError(f"Failed to get journal comment count: {e}")
    
    def mark_journal_comments_as_read(self, *journal_ids) -> bool:
        """Mark journal comments as read"""
        try:
            if not journal_ids:
                return False
            
            for journal_id in journal_ids:
                JournalComment.query.filter_by(journal_id=journal_id).update({"is_read": True})
            
            database.session.commit()
            return True
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to mark comments as read: {e}")
    
    # Journal like operations
    
    def create_journal_like(self, journal_id: int, author_id: int, 
                           publish_time: Optional[Union[str, datetime]] = None) -> bool:
        """Create a journal like"""
        try:
            if not publish_time:
                publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(publish_time, datetime):
                publish_time = publish_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if like already exists
            existing_like = JournalLike.query.filter_by(journal_id=journal_id, author_id=author_id).first()
            if existing_like:
                return False
            
            like = JournalLike(journal_id=journal_id, author_id=author_id, publish_time=publish_time)
            database.session.add(like)
            database.session.commit()
            
            return True
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to create journal like: {e}")
    
    def get_journal_likes(self, journal_id: int) -> List[JournalLikeData]:
        """Get journal likes"""
        try:
            likes = JournalLike.query.filter_by(journal_id=journal_id).all()
            return [extract_journal_like_data(like) for like in likes]
        except Exception as e:
            raise DatabaseError(f"Failed to get journal likes: {e}")
    
    def get_journal_like_count(self, journal_id: int) -> int:
        """Get journal like count"""
        try:
            return JournalLike.query.filter_by(journal_id=journal_id).count()
        except Exception as e:
            raise DatabaseError(f"Failed to get journal like count: {e}")
    
    # Book operations
    
    def create_book(self, isbn: str, title: str, origin_title: Optional[str], subtitle: Optional[str],
                   author: str, page: Optional[int], publish_date: Optional[Union[str, datetime]],
                   publisher: Optional[str], description: Optional[str], douban_score: Optional[float],
                   douban_id: Optional[str], bangumi_score: Optional[float], bangumi_id: Optional[str],
                   book_type: Optional[str]) -> Union[bool, int]:
        """Create a new book"""
        try:
            if not title or not author or not isbn:
                return False
            
            # Check if book already exists
            existing_book = Book.query.filter(
                (Book.title == title) & (Book.author == author) |
                (Book.isbn == isbn)
            ).first()
            
            if existing_book:
                return False
            
            book = Book(
                isbn=isbn, title=title, origin_title=origin_title, subtitle=subtitle,
                author=author, page=page, publish_date=publish_date, publisher=publisher,
                description=description, douban_score=douban_score, douban_id=douban_id,
                bangumi_score=bangumi_score, bangumi_id=bangumi_id, type_=book_type
            )
            
            database.session.add(book)
            database.session.commit()
            
            return book.id
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to create book: {e}")
    
    def get_book(self, limit: int = 1, **filters) -> Union[List[BookData], BookData, None]:
        """Get book information"""
        try:
            # Build query
            if filters and "keyword" in filters:
                keyword = filters.get('keyword')
                query = Book.query.filter(
                    Book.title.like(f"%{keyword}%") |
                    Book.subtitle.like(f"%{keyword}%") |
                    Book.author.like(f"%{keyword}%")
                )
            else:
                filter_dict = {k: v for k, v in filters.items() if k != 'keyword'}
                query = Book.query.filter_by(**filter_dict) if filter_dict else Book.query
            
            # Execute query
            if limit == 1:
                book = query.first()
                return extract_book_data(book) if book else None
            elif limit > 1:
                books = query.limit(limit).all()
                return [extract_book_data(book) for book in books]
            else:
                books = query.all()
                return [extract_book_data(book) for book in books]
                
        except Exception as e:
            raise DatabaseError(f"Failed to get book: {e}")
    
    def update_book(self, book_id: int, **kwargs) -> bool:
        """Update book information"""
        try:
            book = Book.query.filter_by(id=book_id).first()
            if not book:
                return False
            
            for key, value in kwargs.items():
                if hasattr(book, key):
                    if value == "":
                        value = None
                    setattr(book, key, value)
            
            database.session.commit()
            return True
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to update book: {e}")
    
    # Group operations
    
    def create_group(self, name: str, description: str, founder_id: int,
                    establish_time: Optional[Union[datetime, str]] = None) -> Union[int, Literal[False]]:
        """Create a new group"""
        try:
            if not establish_time:
                establish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(establish_time, datetime):
                establish_time = establish_time.strftime("%Y-%m-%d %H:%M:%S")
            
            group = Group(name=name, description=description, founder_id=founder_id, establish_time=establish_time)
            database.session.add(group)
            database.session.commit()
            
            return group.id
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to create group: {e}")
    
    def get_group(self, limit: int = 1, **filters) -> Union[List[GroupData], GroupData, None]:
        """Get group information"""
        try:
            # Build query
            if filters and "keyword" in filters:
                keyword = filters.get('keyword')
                query = Group.query.filter(
                    Group.name.like(f"%{keyword}%") |
                    Group.description.like(f"%{keyword}%")
                )
            else:
                filter_dict = {k: v for k, v in filters.items() if k != 'keyword'}
                query = Group.query.filter_by(**filter_dict) if filter_dict else Group.query
            
            query = query.order_by(Group.establish_time.desc())
            
            # Execute query
            if limit == 1:
                group = query.first()
                return extract_group_data(group) if group else None
            elif limit > 1:
                groups = query.limit(limit).all()
                return [extract_group_data(group) for group in groups]
            else:
                groups = query.all()
                return [extract_group_data(group) for group in groups]
                
        except Exception as e:
            raise DatabaseError(f"Failed to get group: {e}")
    
    def update_group(self, group_id: int, **kwargs) -> bool:
        """Update group information"""
        try:
            group = Group.query.filter_by(id=group_id).first()
            if not group:
                return False
            
            for key, value in kwargs.items():
                if hasattr(group, key):
                    if value == "":
                        value = None
                    setattr(group, key, value)
            
            database.session.commit()
            return True
            
        except Exception as e:
            database.session.rollback()
            raise DatabaseError(f"Failed to update group: {e}")
    
    # Additional methods would go here for:
    # - Group discussion operations
    # - Group user operations  
    # - Chat operations
    # - Error operations
    # - Message aggregation operations
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get database health status"""
        try:
            # Test database connection
            database.session.execute('SELECT 1')
            
            # Test cache connection
            cache_healthy = self.cache.health_check()
            
            return {
                'database': 'healthy',
                'cache': 'healthy' if cache_healthy else 'unhealthy',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {
                'database': 'unhealthy',
                'cache': 'unknown',
                'error': str(e),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            } 