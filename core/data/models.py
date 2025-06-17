"""
Data Models Module
Defines all database models using SQLAlchemy ORM with modern Python features
"""
from datetime import datetime
from typing import Union, Optional
from enum import Enum

from flask_sqlalchemy import SQLAlchemy

# Database instance
database = SQLAlchemy()


class UserRole(Enum):
    """User role enumeration"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class BookCategory(Enum):
    """Book category enumeration based on Chinese Library Classification"""
    MARXISM = "marxism"
    PHILOSOPHY = "philosophy"
    SOCIAL_SCIENCE = "social_science"
    POLITICS_LAW = "politics_law"
    MILITARY = "military"
    ECONOMICS = "economics"
    CULTURE_EDUCATION = "culture_education"
    LANGUAGE = "language"
    LITERATURE = "literature"
    ART = "art"
    HISTORY_GEOGRAPHY = "history_geography"
    NATURAL_SCIENCE = "natural_science"
    MATHEMATICS_CHEMISTRY = "mathematics_chemistry"
    ASTRONOMY_EARTH = "astronomy_earth"
    BIOLOGY = "biology"
    MEDICINE = "medicine"
    AGRICULTURE = "agriculture"
    TECHNOLOGY = "technology"
    TRANSPORTATION = "transportation"
    AVIATION_AEROSPACE = "aviation_aerospace"
    ENVIRONMENT = "environment"
    COMPREHENSIVE = "comprehensive"


class BaseModel:
    """Base model with common functionality"""
    
    def to_dict(self, exclude_fields: Optional[list] = None) -> dict:
        """Convert model instance to dictionary"""
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value, Enum):
                    value = value.value
                result[column.name] = value
        
        return result


class User(database.Model, BaseModel):
    """User model for platform users"""
    __tablename__ = 'user'
    
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    account = database.Column(database.String(24), unique=True, nullable=False)
    password = database.Column(database.Text, nullable=False)
    signature = database.Column(database.String(128), nullable=True)
    email = database.Column(database.String(120), nullable=True)
    telephone = database.Column(database.String(11), nullable=True)
    role = database.Column(database.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    
    # Relationships
    journals = database.relationship('Journal', backref='author', lazy=True)
    journal_comments = database.relationship('JournalComment', backref='comment_author', lazy=True)
    journal_likes = database.relationship('JournalLike', backref='like_author', lazy=True)
    founded_groups = database.relationship('Group', backref='founder', lazy=True)
    
    def __init__(self, account: str, password: str, signature: Optional[str] = None, 
                 email: Optional[str] = None, telephone: Optional[str] = None, 
                 role: UserRole = UserRole.STUDENT):
        self.account = account
        self.password = password
        self.signature = signature or ""
        self.email = email
        self.telephone = telephone
        self.role = role
    
    def __repr__(self):
        return f'<User {self.account}>'


class Book(database.Model, BaseModel):
    """Book model for book information"""
    __tablename__ = 'book'
    
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    isbn = database.Column(database.String(32), unique=True, nullable=True)
    title = database.Column(database.String(128), nullable=False)
    origin_title = database.Column(database.String(128), nullable=True)
    subtitle = database.Column(database.String(128), nullable=True)
    author = database.Column(database.String(128), nullable=False)
    page = database.Column(database.Integer, nullable=True)
    publish_date = database.Column(database.Date, nullable=True)
    publisher = database.Column(database.String(32), nullable=True)
    description = database.Column(database.Text, nullable=True)
    douban_score = database.Column(database.Float, nullable=True)
    douban_id = database.Column(database.String(24), nullable=True)
    bangumi_score = database.Column(database.Float, nullable=True)
    bangumi_id = database.Column(database.String(24), nullable=True)
    type = database.Column(database.String(128), nullable=True)
    
    # Relationships
    journals = database.relationship('Journal', backref='book', lazy=True)
    
    def __init__(self, isbn: Optional[str], title: str, origin_title: Optional[str], 
                 subtitle: Optional[str], author: str, page: Optional[int],
                 publish_date: Optional[Union[str, datetime]], publisher: Optional[str], 
                 description: Optional[str], douban_score: Optional[float], 
                 douban_id: Optional[str], bangumi_score: Optional[float], 
                 bangumi_id: Optional[str], type_: Optional[str]):
        self.isbn = isbn
        self.title = title
        self.origin_title = origin_title
        self.subtitle = subtitle
        self.author = author
        self.page = page
        
        if publish_date:
            if isinstance(publish_date, datetime):
                self.publish_date = publish_date.date()
            else:
                self.publish_date = datetime.strptime(publish_date, "%Y-%m-%d").date()
        else:
            self.publish_date = None
            
        self.publisher = publisher
        self.description = description
        self.douban_score = douban_score
        self.douban_id = douban_id
        self.bangumi_score = bangumi_score
        self.bangumi_id = bangumi_id
        self.type = type_
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'


class Journal(database.Model, BaseModel):
    """Journal model for book reviews"""
    __tablename__ = 'journal'
    
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    title = database.Column(database.String(128), nullable=False)
    first_paragraph = database.Column(database.Text, nullable=False)
    content = database.Column(database.Text, nullable=False)
    publish_time = database.Column(database.DateTime, nullable=False)
    author_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    book_id = database.Column(database.Integer, database.ForeignKey('book.id'), nullable=False)
    
    # Relationships
    comments = database.relationship('JournalComment', backref='journal', lazy=True, cascade='all, delete-orphan')
    likes = database.relationship('JournalLike', backref='journal', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, title: str, first_paragraph: str, content: str, 
                 publish_time: Union[str, datetime], author_id: int, book_id: int):
        self.title = title
        self.first_paragraph = first_paragraph
        self.content = content
        
        if isinstance(publish_time, datetime):
            self.publish_time = publish_time
        else:
            self.publish_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
            
        self.author_id = author_id
        self.book_id = book_id
    
    def __repr__(self):
        return f'<Journal {self.title}>'


class JournalComment(database.Model, BaseModel):
    """Journal comment model"""
    __tablename__ = 'journal_comment'
    
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    publish_time = database.Column(database.DateTime, nullable=False)
    author_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    journal_id = database.Column(database.Integer, database.ForeignKey('journal.id'), nullable=False)
    content = database.Column(database.Text, nullable=False)
    is_read = database.Column(database.Boolean, nullable=False, default=False)
    
    def __init__(self, publish_time: Union[str, datetime], author_id: int, 
                 journal_id: int, content: str, is_read: bool = False):
        if isinstance(publish_time, datetime):
            self.publish_time = publish_time
        else:
            self.publish_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
            
        self.author_id = author_id
        self.journal_id = journal_id
        self.content = content if isinstance(content, str) else "\n".join(content)
        self.is_read = is_read
    
    def __repr__(self):
        return f'<JournalComment on Journal {self.journal_id}>'


class JournalLike(database.Model, BaseModel):
    """Journal like model"""
    __tablename__ = 'journal_like'
    
    author_id = database.Column(database.Integer, database.ForeignKey('user.id'), primary_key=True)
    journal_id = database.Column(database.Integer, database.ForeignKey('journal.id'), primary_key=True)
    publish_time = database.Column(database.DateTime, nullable=False)
    
    def __init__(self, author_id: int, journal_id: int, 
                 publish_time: Union[str, datetime]):
        self.author_id = author_id
        self.journal_id = journal_id
        
        if isinstance(publish_time, datetime):
            self.publish_time = publish_time
        else:
            self.publish_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
    
    def __repr__(self):
        return f'<JournalLike by User {self.author_id} on Journal {self.journal_id}>'


class Group(database.Model, BaseModel):
    """Group model for reading groups"""
    __tablename__ = 'group'
    
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String(32), unique=True, nullable=False)
    founder_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    establish_time = database.Column(database.DateTime, nullable=False)
    description = database.Column(database.Text, nullable=True)
    
    # Relationships
    discussions = database.relationship('GroupDiscussion', backref='group', lazy=True, cascade='all, delete-orphan')
    members = database.relationship('GroupUser', backref='group', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name: str, founder_id: int, description: Optional[str], 
                 establish_time: Union[str, datetime]):
        self.name = name
        self.founder_id = founder_id
        self.description = description
        
        if isinstance(establish_time, datetime):
            self.establish_time = establish_time
        else:
            self.establish_time = datetime.strptime(establish_time, "%Y-%m-%d %H:%M:%S")
    
    def __repr__(self):
        return f'<Group {self.name}>'


class GroupDiscussion(database.Model, BaseModel):
    """Group discussion model"""
    __tablename__ = 'group_discussion'
    
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    poster_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    group_id = database.Column(database.Integer, database.ForeignKey('group.id'), nullable=False)
    post_time = database.Column(database.DateTime, nullable=False)
    title = database.Column(database.String(256), nullable=False)
    content = database.Column(database.Text, nullable=False)
    is_read = database.Column(database.Boolean, nullable=False, default=False)
    
    # Relationships
    replies = database.relationship('GroupDiscussionReply', backref='discussion', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, poster_id: int, group_id: int, post_time: Union[str, datetime], 
                 title: str, content: str, is_read: bool = False):
        self.poster_id = poster_id
        self.group_id = group_id
        
        if isinstance(post_time, datetime):
            self.post_time = post_time
        else:
            self.post_time = datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
            
        self.title = title
        self.content = content
        self.is_read = is_read
    
    def __repr__(self):
        return f'<GroupDiscussion {self.title}>'


class GroupDiscussionReply(database.Model, BaseModel):
    """Group discussion reply model"""
    __tablename__ = 'group_discussion_reply'
    
    author_id = database.Column(database.Integer, database.ForeignKey('user.id'), primary_key=True)
    discussion_id = database.Column(database.Integer, database.ForeignKey('group_discussion.id'), primary_key=True)
    reply_time = database.Column(database.DateTime, primary_key=True)
    content = database.Column(database.Text, nullable=False)
    is_read = database.Column(database.Boolean, nullable=False, default=False)
    
    def __init__(self, author_id: int, discussion_id: int, reply_time: Union[str, datetime], 
                 content: str, is_read: bool = False):
        self.author_id = author_id
        self.discussion_id = discussion_id
        
        if isinstance(reply_time, datetime):
            self.reply_time = reply_time
        else:
            self.reply_time = datetime.strptime(reply_time, "%Y-%m-%d %H:%M:%S")
            
        self.content = content
        self.is_read = is_read
    
    def __repr__(self):
        return f'<GroupDiscussionReply on Discussion {self.discussion_id}>'


class GroupUser(database.Model, BaseModel):
    """Group user membership model"""
    __tablename__ = 'group_user'
    
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), primary_key=True)
    group_id = database.Column(database.Integer, database.ForeignKey('group.id'), primary_key=True)
    join_time = database.Column(database.DateTime, nullable=False)
    
    # Relationships
    user = database.relationship('User', backref='group_memberships')
    
    def __init__(self, user_id: int, group_id: int, join_time: Union[str, datetime]):
        self.user_id = user_id
        self.group_id = group_id
        
        if isinstance(join_time, datetime):
            self.join_time = join_time
        else:
            self.join_time = datetime.strptime(join_time, "%Y-%m-%d %H:%M:%S")
    
    def __repr__(self):
        return f'<GroupUser User {self.user_id} in Group {self.group_id}>'


class Chat(database.Model, BaseModel):
    """Chat model for private messages"""
    __tablename__ = 'chat'
    
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    sender_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    receiver_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    content = database.Column(database.Text, nullable=False)
    send_time = database.Column(database.DateTime, nullable=False)
    is_read = database.Column(database.Boolean, nullable=False, default=False)
    
    # Relationships
    sender = database.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = database.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    
    def __init__(self, sender_id: int, receiver_id: int, content: str, 
                 send_time: Union[str, datetime], is_read: bool = False):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        
        if isinstance(send_time, datetime):
            self.send_time = send_time
        else:
            self.send_time = datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S")
            
        self.is_read = is_read
    
    def __repr__(self):
        return f'<Chat from User {self.sender_id} to User {self.receiver_id}>'


class Error(database.Model, BaseModel):
    """Error model for custom error pages"""
    __tablename__ = 'error'
    
    error_code = database.Column(database.Integer, primary_key=True)
    title = database.Column(database.String(128), nullable=False)
    title_en = database.Column(database.String(128), nullable=True)
    content = database.Column(database.Text, nullable=True)
    publish_time = database.Column(database.DateTime, nullable=True)
    reference_link = database.Column(database.String(128), nullable=True)
    
    def __init__(self, error_code: int, title: str, title_en: Optional[str], 
                 content: Optional[str], publish_time: Union[str, datetime], 
                 reference_link: Optional[str]):
        self.error_code = error_code
        self.title = title
        self.title_en = title_en
        self.content = content
        
        if publish_time:
            if isinstance(publish_time, datetime):
                self.publish_time = publish_time
            else:
                self.publish_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
        else:
            self.publish_time = None
            
        self.reference_link = reference_link
    
    def __repr__(self):
        return f'<Error {self.error_code}: {self.title}>' 