"""数据模型"""
from typing import Union

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Book(db.Model):
    """图书 表 数据模型"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(32), unique=True)
    title = db.Column(db.String(128), unique=False)
    origin_title = db.Column(db.String(128), unique=False)
    subtitle = db.Column(db.String(128), unique=False)
    author = db.Column(db.String(128), unique=False)
    page = db.Column(db.Integer, unique=False)
    publish_date = db.Column(db.Date, unique=False)
    publisher = db.Column(db.String(32), unique=False)
    description = db.Column(db.Text, unique=False)
    douban_score = db.Column(db.Float, unique=False)
    douban_id = db.Column(db.String(24), unique=False)
    bangumi_score = db.Column(db.Float, unique=False)
    bangumi_id = db.Column(db.String(24), unique=False)
    type = db.Column(
        db.Enum("马列主义、毛泽东思想、邓小平理论", "哲学、宗教", "社会科学总论", "政治、法律", "军事", "经济",
                "文化、科学、教育、体育", "语言、文字", "文学", "艺术", "历史、地理", "自然科学总论",
                "数理科学和化学", "天文学、地球科学", "生物科学", "医药、卫生", "农业科学", "工业技术",
                "交通运输", "航空、航天", "环境科学、安全科学", "综合性图书"), unique=False)

    def __init__(self, isbn, title, origin_title, subtitle, author, page, publish_date, publisher, description,
                 douban_score, douban_id, bangumi_score, bangumi_id, type_):
        self.isbn = isbn
        self.title = title
        self.origin_title = origin_title if origin_title else None
        self.subtitle = subtitle if subtitle else None
        self.author = author
        self.page = page if page else None
        if not publish_date:
            self.publish_date = None
        else:
            if isinstance(publish_date, datetime):
                self.publish_date = publish_date
            else:
                self.publish_date = datetime.strptime(publish_date, "%Y-%m-%d")
        self.publisher = publisher if publisher else None
        self.description = description if description else None
        self.douban_score = douban_score if douban_score else None
        self.douban_id = douban_id if douban_id else None
        self.bangumi_score = bangumi_score if bangumi_score else None
        self.bangumi_id = bangumi_id if bangumi_id else None
        self.type = type_ if type_ else None


class Chat(db.Model):
    """站内私信 表 数据模型"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.DateTime, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, sender_id, receiver_id, content, send_time, is_read=False):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        if not send_time:
            self.send_time = None
        else:
            if isinstance(send_time, datetime):
                self.send_time = send_time
            else:
                self.send_time = datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S")
        self.is_read = is_read


class Error(db.Model):
    """错误码及描述 表 数据模型"""
    error_code = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), unique=False)
    title_en = db.Column(db.String(128), unique=False)
    content = db.Column(db.Text, unique=False)
    publish_time = db.Column(db.DateTime, unique=False)
    reference_link = db.Column(db.String(128), unique=False)

    def __init__(self, error_code, title, title_en, content, publish_time, reference_link):
        self.error_code = error_code
        self.title = title
        self.title_en = title_en
        self.content = content
        if not publish_time:
            self.publish_time = None
        else:
            if isinstance(publish_time, datetime):
                self.publish_time = publish_time
            else:
                self.publish_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
        self.reference_link = reference_link


class Group(db.Model):
    """圈子 表 数据模型"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True)
    founder_id = db.Column(db.Integer, unique=False)
    establish_time = db.Column(db.DateTime, unique=False)
    description = db.Column(db.Text, unique=False)

    def __init__(self, name, founder_id, description, establish_time):
        self.name = name
        self.founder_id = founder_id
        self.description = description
        if not establish_time:
            self.establish_time = None
        else:
            if isinstance(establish_time, datetime):
                self.establish_time = establish_time
            else:
                self.establish_time = datetime.strptime(establish_time, "%Y-%m-%d %H:%M:%S")


class GroupDiscussion(db.Model):
    """圈子-讨论 表 数据模型"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poster_id = db.Column(db.Integer, unique=False)
    group_id = db.Column(db.Integer, unique=False)
    post_time = db.Column(db.DateTime, unique=False)
    title = db.Column(db.String(256), unique=False)
    content = db.Column(db.Text, unique=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, poster_id: int, group_id: int, post_time: Union[str, datetime], title: str, content: str,
                 is_read=False):
        self.poster_id = poster_id
        self.group_id = group_id
        if not post_time:
            self.post_time = None
        else:
            if isinstance(post_time, datetime):
                self.post_time = post_time
            else:
                self.post_time = datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
        self.title = title
        self.content = content
        self.is_read = is_read


class GroupDiscussionReply(db.Model):
    """圈子-讨论-回复 表 数据模型"""
    author_id = db.Column(db.Integer, unique=False)
    discussion_id = db.Column(db.Integer, unique=False)
    reply_time = db.Column(db.DateTime, unique=False)
    __table_args__ = (db.PrimaryKeyConstraint('author_id', 'discussion_id', 'reply_time'),)  # 联合主键
    content = db.Column(db.Text, unique=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, author_id: int, discussion_id: int, reply_time, content, is_read=False):
        self.author_id = author_id
        self.discussion_id = discussion_id
        if not reply_time:
            self.reply_time = None
        else:
            if isinstance(reply_time, datetime):
                self.reply_time = reply_time
            else:
                self.reply_time = datetime.strptime(reply_time, "%Y-%m-%d %H:%M:%S")
        self.content = content
        self.is_read = is_read


class GroupUser(db.Model):
    """圈子-成员 表 数据模型"""
    user_id = db.Column(db.Integer, unique=False)
    group_id = db.Column(db.Integer, unique=False)
    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'group_id'),)  # 联合主键
    join_time = db.Column(db.DateTime, unique=False)

    def __init__(self, user_id, group_id, join_time):
        self.user_id = user_id
        self.group_id = group_id
        if not join_time:
            self.join_time = None
        else:
            if isinstance(join_time, datetime):
                self.join_time = join_time
            else:
                self.join_time = datetime.strptime(join_time, "%Y-%m-%d %H:%M:%S")


class User(db.Model):
    """用户 表 数据模型"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account = db.Column(db.String(24), unique=True)
    password = db.Column(db.Text, unique=False)
    signature = db.Column(db.String(128), unique=False)
    email = db.Column(db.String(120), unique=False)
    telephone = db.Column(db.String(11), unique=False)
    role = db.Column(db.Enum("student", "teacher", "admin"), unique=False)

    def __init__(self, account: str, password: str, signature: str, email: str, telephone: str, role: str = "student"):
        self.account = account
        self.password = password
        self.signature = signature if signature else None
        self.email = email if email else None
        self.telephone = telephone if telephone else None
        self.role = role


class Journal(db.Model):
    """书评 表 数据模型"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), unique=False)
    first_paragraph = db.Column(db.Text, unique=False)
    content = db.Column(db.Text, unique=False)
    publish_time = db.Column(db.DateTime, unique=False)
    author_id = db.Column(db.Integer, unique=False)
    book_id = db.Column(db.Integer, unique=False)

    def __init__(self, title: str, first_paragraph: str, content: str, publish_time, author_id: int, book_id: int):
        self.title = title
        self.first_paragraph = first_paragraph
        self.content = content
        if not publish_time:
            self.publish_time = None
        else:
            if isinstance(publish_time, datetime):
                self.publish_time = publish_time
            else:
                self.publish_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
        self.author_id = author_id
        self.book_id = book_id


class JournalComment(db.Model):
    """书评-评论 表 数据模型"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    publish_time = db.Column(db.DateTime, unique=False)
    author_id = db.Column(db.Integer, unique=False)
    journal_id = db.Column(db.Integer, unique=False)
    content = db.Column(db.Text, unique=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, publish_time, author_id: int, journal_id: int, content: Union[str, list], is_read=False):
        if not publish_time:
            self.publish_time = None
        else:
            if isinstance(publish_time, datetime):
                self.publish_time = publish_time
            else:
                self.publish_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
        self.author_id = author_id
        self.journal_id = journal_id
        self.content = content if isinstance(content, str) else "\n".join(content)
        self.is_read = is_read


class JournalLike(db.Model):
    """书评-点赞 表 数据模型"""
    author_id = db.Column(db.Integer, unique=False)
    journal_id = db.Column(db.Integer, unique=False)
    __table_args__ = (db.PrimaryKeyConstraint('author_id', 'journal_id'),)  # 让authorID和journalID作为联合主键
    publish_time = db.Column(db.DateTime, unique=False)

    def __init__(self, author_id: int, journal_id: int, publish_time):
        self.author_id = author_id
        self.journal_id = journal_id
        if not publish_time:
            self.publish_time = None
        else:
            if isinstance(publish_time, datetime):
                self.publish_time = publish_time
            else:
                self.publish_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
