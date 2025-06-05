"""数据持久层，与数据库交互"""

from flask import Flask
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from service.database.Redis import Cache
from service.database.Utils import *
from service.Utils import Config
from typing import Union, Literal

class Database:
    """
    基本函数类别：get__(), add__(), modify__(), delete__()
    """

    def __init__(self, app: Flask):
        info = Config.get("Database")
        client = f"{info['Type'].lower()}+{info['Driver']}"
        host = info["Host"]
        port = info["Port"]
        account = info["Account"]
        password = info["Password"]
        database = info["Database"]
        URI = f"{client}://{account}:{password}@{host}:{port}/{database}"
        app.config["SQLALCHEMY_DATABASE_URI"] = URI
        db.init_app(app)
        self.cache = Cache(**Config.get("Redis"))

    """User相关"""

    @staticmethod
    def addUser(account: str, raw_password: str, email: str, telephone: str, role: str = "student") -> int:
        """
        添加用户
        :param account: 用户名
        :param raw_password: 密码(明文)
        :param email: 邮箱
        :param telephone: 电话
        :param role: 角色身份
        :return: user_id
        """
        email = None if email == "" else email
        telephone = None if telephone == "" else telephone
        user = User(
            account=account,
            password=generate_password_hash(raw_password),
            signature="",
            email=email,
            telephone=telephone,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return user.id

    def modifyUser(self, filter_id: int = None, filter_account: str = None, **kwargs) -> bool:
        """
        修改用户信息
        :param filter_id: 用于确定用户的id
        :param filter_account: 用于确定用户的account
        :param kwargs: 用于修改的参数，包括User的全部字段
        :return: 是否成功修改
        """
        if filter_id:
            user = User.query.filter_by(id=filter_id).first()
        elif filter_account:
            user = User.query.filter_by(account=filter_account).first()
        else:
            return False
        if not user:
            return False
        self.cache.modifyUser(user.id, **kwargs)
        for key in kwargs:
            if hasattr(user, key):
                if key != "password":
                    setattr(user, key, kwargs[key])
                else:
                    setattr(user, key, generate_password_hash(kwargs[key]))
        db.session.commit()
        return True

    def getUser(self, limit: int = 1, with_password: bool = False, **filters) -> Union[
        list[UserDict], UserDict, list[None], None
    ]:
        """
        获取用户信息
        :param limit: 限制返回的数量，默认为1即返回单个用户信息，其他正值为限制量，0、负值、None为不限制
        :param with_password: 是否返回密码，默认为False，此时返回值的password字段为None
        :param filters: 用于筛选的参数，包括User的全部字段和"keyword"字段(用于模糊搜索)
        :return: 用户信息(UserDict或list[UserDict])
        """
        if "id" in filters and limit == 1:  # 仅当通过id获取单个用户时，才会使用缓存
            cache_res = self.cache.getUser(filters["id"], with_password)
            if cache_res:
                return cache_res
        if filters and "keyword" in filters:
            users = User.query.filter(User.account.like(f"%{filters.get('keyword')}%"))
        else:
            users = User.query.filter_by(**filters) if filters else User.query
        if limit == 1:
            user = users.first()
            res = extractUser(user, with_password) if user else None
            self.cache.setUser(res)
            return res
        elif limit > 1:
            users = users.limit(limit).all()
            res = [extractUser(user, with_password) for user in users]
            self.cache.setUser(res)
            return res
        else:
            users = users.all()
            res = [extractUser(user, with_password) for user in users]
            self.cache.setUser(res)
            return res

    def checkLogin(self, account: str, password: str) -> Union[int, bool]:
        """
        检查登录信息是否正确
        :param account: 用户名
        :param password: 密码(明文)
        :return: 用户id(登录成功)或False(登录失败)
        """
        users_info = self.getUser(limit=0, with_password=True, account=account)
        if len(users_info) == 0:
            return False
        else:
            for info in users_info:
                if check_password_hash(info.get("password"), password):
                    return info["id"]
            else:
                return False

    """Journal相关"""

    def addJournal(self, title: str, content: Union[list, str], publish_time: str, author_id: int, book_id: int) -> int:
        """
        添加书评
        :param title: 书评标题
        :param content: 书评内容
        :param publish_time: 发表时间
        :param author_id: 作者id
        :param book_id: 书籍id
        :return: journal_id
        """
        if isinstance(content, list):
            _content: str = "\n".join(content)
            _first_paragraph: str = content[0]
        else:  # content为str
            _content = content
            _first_paragraph = content.split("\n")[0]
        journal = Journal(
            title=title,
            first_paragraph=_first_paragraph,
            content=_content,
            publish_time=publish_time,
            author_id=author_id,
            book_id=book_id
        )
        db.session.add(journal)
        db.session.commit()
        journal_dict = extractJournal(Journal.query.filter_by(title=title, author_id=author_id).first())
        journal_dict['content'] = content.split("\n")
        self.cache.setJournal(journal_dict)
        return journal_dict.get('id')

    def getJournal(self, limit: int = 1, **filters) -> Union[list[JournalDict], JournalDict, list[None], None]:
        """
        获取书评信息
        :param limit: 限制返回的数量，默认为1即返回单个书评信息，其他正值为限制量，0、负值、None为不限制
        :param filters: 用于筛选的参数，包括Journal的全部字段和"keyword"字段(用于模糊搜索)
        :return: 书评信息(JournalDict或list[JournalDict])
        """
        if "id" in filters and limit == 1:  # 仅当通过id获取单个书评时，才会使用缓存
            cache_res = self.cache.getJournal(filters.get('id'))
            if cache_res:
                return cache_res
        if filters and "keyword" in filters:
            related_book = self.getBook(keyword=filters.get('keyword'))
            if related_book:
                journals = Journal.query.filter(
                    Journal.title.like(f"%{filters.get('keyword')}%") |
                    Journal.content.like(f"%{filters.get('keyword')}%") |
                    (Journal.book_id == related_book.get('id'))
                )
            else:
                journals = Journal.query.filter(
                    Journal.title.like(f"%{filters.get('keyword')}%") |
                    Journal.content.like(f"%{filters.get('keyword')}%")
                )
        else:
            journals = Journal.query.filter_by(**filters) if filters else Journal.query
        if limit == 1:
            journal = journals.first()
            res = extractJournal(
                journal,
                self.getJournalCommentsNum(journal_id=journal.id),
                self.getJournalLikesNum(journal.id)
            ) if journal else None
        elif limit > 1:
            journals = journals.limit(limit).all()
            res = [extractJournal(
                journal,
                self.getJournalCommentsNum(journal_id=journal.id),
                self.getJournalLikesNum(journal.id)
            ) for journal in journals if journal]
        else:
            journals = journals.all()
            res = [extractJournal(
                journal,
                JournalComment.query.filter_by(journal_id=journal.id).count(),
                JournalLike.query.filter_by(journal_id=journal.id).count()
            ) for journal in journals if journal]
        self.cache.setJournal(res)
        return res

    """JournalComment相关"""

    def addJournalComment(
            self, journal_id: int, content: Union[str, list], author_id: int, publish_time: str = None
    ) -> int:
        """
        添加书评评论
        :param journal_id: 书评id
        :param content: 评论内容
        :param author_id: 评论者id
        :param publish_time: 发表时间
        :return: comment_id
        """
        if not publish_time:
            publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comment = JournalComment(
            publish_time=publish_time,
            author_id=author_id,
            journal_id=journal_id,
            content=content
        )
        if author_id == Journal.query.filter_by(id=journal_id).first().author_id:
            comment.is_read = True  # 如果是作者自己回复，自动标记为已读
        db.session.add(comment)
        db.session.commit()
        comment_dict = extractJournalComment(
            JournalComment.query.filter_by(
                author_id=author_id, journal_id=journal_id, publish_time=publish_time
            ).first()
        )
        self.cache.setJournalComment(comment_dict)
        return comment_dict.get("id")

    def markJournalCommentsAsRead(self, *journals_id) -> bool:
        """
        将Journal的所有Comments都标记为已读
        :param journals_id: Journal的id，可以传入多个
        :return: 是否成功标记
        """
        if not journals_id:
            return False
        for journal_id in journals_id:
            JournalComment.query.filter_by(journal_id=journal_id).update({"is_read": True})
            self.cache.markJournalCommentsAsRead(journal_id)
        db.session.commit()
        return True

    def getJournalComment(self, **filters) -> Union[list[JournalCommentDict], list[None]]:
        """
        获取全部关于journal_id的comment
        :param filters: 用于筛选的参数，包括JournalComment的全部字段
        :return: 评论信息(JournalCommentDict或list[JournalCommentDict])
        """
        if "journal_id" in filters:
            cache_res = self.cache.getJournalComment(filters.get("journal_id"))
            if cache_res:
                return cache_res
        comments = JournalComment.query.filter_by(**filters).order_by(JournalComment.publish_time.asc()).all()
        if not comments:
            return []
        else:
            res = [extractJournalComment(comment) for comment in comments]
            self.cache.setJournalComment(res)
            return res

    def getJournalCommentsNum(self, **filters) -> int:
        """
        获取关于journal_id的评论数
        :param filters: 用于筛选的参数，包括JournalComment的全部字段
        :return: 评论数
        """
        if "journal_id" in filters:
            cache_res = self.cache.getJournalComment(filters.get("journal_id"))
            if cache_res:
                return len(cache_res)
        return len(self.getJournalComment(**filters))

    """JournalLike相关"""

    def addJournalLike(
            self, journal_id: int, author_id: Union[int, str], publish_time: Union[str, datetime] = None
    ) -> bool:
        """
        根据journal_id和author_id添加点赞记录
        :param journal_id: 书评id
        :param author_id: 点赞者id
        :param publish_time: 发表时间
        :return: 是否成功添加点赞记录(False说明已经存在该点赞记录)
        """
        if not publish_time:
            publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(publish_time, datetime):
            publish_time = publish_time.strftime("%Y-%m-%d %H:%M:%S")
        if self.cache.getJournalLike(journal_id):  # 如果在缓存或数据库中已经存在该点赞记录，则返回False
            return False
        if JournalLike.query.filter_by(journal_id=journal_id, author_id=author_id).first():
            return False
        else:
            like = JournalLike(journal_id=journal_id, author_id=author_id, publish_time=publish_time)
            db.session.add(like)
            db.session.commit()
            self.cache.setJournalLike(extractJournalLike(like))
            return True

    def getJournalLike(self, journal_id: int) -> Union[list[JournalLikeDict], list[None]]:
        """
        根据journal_id获取所有点赞记录
        :param journal_id: 书评id
        :return: 点赞信息(JournalLikeDict或list[JournalLikeDict])
        """
        cache_res = self.cache.getJournalLike(journal_id)
        if cache_res:
            return cache_res
        likes = JournalLike.query.filter_by(journal_id=journal_id).all()
        if not likes:
            return []
        else:
            res = [extractJournalLike(like) for like in likes]
            self.cache.setJournalLike(res)
            return res

    def getJournalLikesNum(self, journal_id: int) -> int:
        """
        根据journal_id获取点赞数
        :param journal_id: 书评id
        :return: 点赞数
        """
        cache_res = self.cache.getJournalLike(journal_id)
        if cache_res:
            return len(cache_res)
        return len(self.getJournalLike(journal_id))

    """Book相关"""

    def addBook(
            self, isbn: str, title: str, origin_title: str, subtitle: str, author: str, page: int,
            publish_date: Union[str, datetime], publisher: str, description: str, douban_score: float, douban_id: int,
            bangumi_score: float, bangumi_id: str, type_: str) -> Union[bool, int]:
        """
        添加书籍
        :param isbn: ISBN编号
        :param title: 书名
        :param origin_title: 原名(如《老人与海》的origin_title字段即为'The Old Man and the Sea')
        :param subtitle: 副标题，如《文化苦旅》的subtitle字段即为'余秋雨三十年散文自选集'
        :param author: 作者
        :param page: 页数
        :param publish_date: 出版日期
        :param publisher: 出版社
        :param description: 书籍简介
        :param douban_score: 豆瓣评分
        :param douban_id: 豆瓣id
        :param bangumi_score: Bangumi评分
        :param bangumi_id: Bangumi id
        :param type_: 书籍类型，依据《中国图书馆图书分类法》分为22个基本大类，详见：https://baike.baidu.com/item/中国图书馆图书分类法/1919634?anchor=4#4
        :return: book_id
        """
        if not title or not author or not isbn:
            return False
        # 检查是否已有该书
        if db.session.query(Book).filter(Book.title == title, Book.author == author).first():
            return False
        if db.session.query(Book).filter(Book.isbn == isbn).first():
            return False
        # 不存在该书，添加
        book = Book(
            isbn=isbn, title=title, origin_title=origin_title, subtitle=subtitle, author=author, page=page,
            publish_date=publish_date, publisher=publisher, description=description, douban_score=douban_score,
            douban_id=douban_id, bangumi_score=bangumi_score, bangumi_id=bangumi_id, type_=type_
        )
        db.session.add(book)
        db.session.commit()
        res = extractBook(Book.query.filter_by(title=title, author=author).first())
        self.cache.setBook(res)
        return res.get('id')

    def modifyBook(self, book_id: int, **kwargs) -> bool:
        """
        根据book_id修改书籍信息
        :param book_id: book_id
        :param kwargs: 用于修改的参数，包括Book的全部字段
        :return: 是否成功修改
        """
        book = Book.query.filter_by(id=book_id).first()
        if not book:
            return False
        self.cache.modifyBook(book_id, **kwargs)
        for key, value in kwargs.items():
            if hasattr(book, key):
                if value == "":
                    value = None
                setattr(book, key, value)
        db.session.commit()
        return True

    def getBook(self, limit: int = 1, **filters) -> Union[list[BookDict], BookDict, list[None], None]:
        """
        获取书籍信息
        :param limit: 限制返回的数量，默认为1即返回单个书籍信息，其他正值为限制量，0、负值、None为不限制
        :param filters: 用于筛选的参数，包括Book的全部字段和"keyword"字段(用于模糊搜索)
        :return: 书籍信息(BookDict或list[BookDict])
        """
        if "id" in filters and limit == 1:  # 仅当通过id获取单个书籍时，才会使用缓存
            cache_res = self.cache.getBook(filters.get("id"))
            if cache_res:
                return cache_res
        if filters and "keyword" in filters:
            books = Book.query.filter(
                Book.title.like(f"%{filters.get('keyword')}%") |
                Book.subtitle.like(f"%{filters.get('keyword')}%") |
                Book.author.like(f"%{filters.get('keyword')}%")
            )
        else:
            books = Book.query.filter_by(**filters) if filters else Book.query
        if limit == 1:
            book = books.first()
            res = extractBook(book) if book else None
        elif limit > 1:
            books = books.limit(limit).all()
            res = [extractBook(book) for book in books]
        else:
            books = books.all()
            res = [extractBook(book) for book in books]
        self.cache.setBook(res)
        return res

    """Group相关"""

    def addGroup(self, name: str, description: str, founder_id: int, establish_time: Union[datetime, str] = None) -> \
            Union[int, Literal[False]]:
        """
        创建一个圈子
        :param name: 圈子名
        :param description: 圈子描述
        :param founder_id: 创建者id
        :param establish_time: 创建时间
        :return: group_id
        """
        if not establish_time:
            establish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(establish_time, datetime):
            establish_time = establish_time.strftime("%Y-%m-%d %H:%M:%S")
        group = Group(name=name, description=description, founder_id=founder_id, establish_time=establish_time)
        db.session.add(group)
        db.session.commit()
        group_dict = extractGroup(Group.query.filter_by(name=name, founder_id=founder_id).first())
        self.cache.setGroup(group_dict)
        return group_dict.get('id')

    def modifyGroup(self, group_id: int, **kwargs) -> bool:
        """
        根据group_id修改圈子信息
        :param group_id: group_id
        :param kwargs: 用于修改的参数，包括Group的全部字段
        :return: 是否修改成功
        """
        group = Group.query.filter_by(id=group_id).first()
        if not group:
            return False
        self.cache.modifyGroup(group_id, **kwargs)
        for key, value in kwargs.items():
            if hasattr(group, key):
                if value == "":
                    value = None
                setattr(group, key, value)
        db.session.commit()
        return True

    def getGroup(self, limit: int = 1, **filters) -> Union[list[GroupDict], GroupDict, list[None], None]:
        """
        获取圈子信息
        :param limit: 限制返回的数量，默认为1即返回单个群组信息，其他正值为限制量，0、负值、None为不限制
        :param filters: 用于筛选的参数，包括Group的全部字段和"keyword"字段(用于模糊搜索)
        """
        if "id" in filters and limit == 1:  # 仅当通过id获取单个圈子时，才会使用缓存
            cache_res = self.cache.getGroup(filters["id"])
            if cache_res:
                return cache_res
        if filters and "keyword" in filters:
            groups = Group.query.filter(
                Group.name.like(f"%{filters.get('keyword')}%") |
                Group.description.like(f"%{filters.get('keyword')}%")
            )
        else:
            groups = Group.query.filter_by(**filters) if filters else Group.query
        groups = groups.order_by(Group.establish_time.desc())
        if limit == 1:
            group = groups.first()
            res = extractGroup(group) if group else None
        elif limit > 1:
            groups = groups.limit(limit).all()
            res = [extractGroup(group) for group in groups]
        else:
            groups = groups.all()
            res = [extractGroup(group) for group in groups]
        self.cache.setGroup(res)
        return res

    """GroupDiscussion相关"""

    def addGroupDiscussion(
            self, poster_id: int, group_id: int, title: str, content: str, post_time: Union[str, datetime] = None
    ) -> int:
        """
        添加帖子
        :param poster_id: 发帖者id
        :param group_id: 圈子的id
        :param post_time: 发布时间
        :param title: 帖子标题
        :param content: 帖子内容
        :return: group_discussion_id
        """
        if not post_time:
            post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(post_time, datetime):
            post_time = post_time.strftime("%Y-%m-%d %H:%M:%S")
        discussion = GroupDiscussion(
            poster_id=poster_id,
            group_id=group_id,
            post_time=post_time if isinstance(post_time, str) else post_time.strftime("%Y-%m-%d %H:%M:%S"),
            title=title,
            content=content
        )
        if poster_id == Group.query.filter_by(id=group_id).first().founder_id:
            discussion.is_read = True  # 如果是圈主发表的帖子，自动标记为已读
        db.session.add(discussion)
        db.session.commit()
        discussion_dict = extractGroupDiscussion(
            GroupDiscussion.query.filter_by(poster_id=poster_id, group_id=group_id, post_time=post_time).first()
        )
        self.cache.setGroupDiscussion(discussion_dict)
        # 检查当前用户是否在group_user中，如不在则自动加入
        users = self.getGroupUser(limit=0, group_id=group_id)
        user_ids = [user.get("user_id") for user in users]
        if poster_id not in user_ids:
            self.addGroupUser(poster_id, group_id)
        return discussion_dict.get("id")

    def getGroupDiscussion(self, limit: int = 1, **filters) -> Union[
        list[GroupDiscussionDict], GroupDiscussionDict, list[None], None
    ]:
        """
        获取圈子内帖子信息
        :param limit: 限制返回的数量，默认为1即返回单个帖子信息，其他正值为限制量，0、负值、None为不限制
        :param filters: 用于筛选的参数，包括GroupDiscussion的全部字段和"keyword"字段(用于模糊搜索)
        :return:
        """
        if "id" in filters and limit == 1:  # 通过id获取单个帖子
            cache_res = self.cache.getGroupDiscussion(discussion_id=filters["id"])
            if cache_res:
                return cache_res
        elif "group_id" in filters and limit == 0:  # 通过group_id获取全部帖子
            cache_res = self.cache.getGroupDiscussion(group_id=filters["group_id"])
            if cache_res:
                return cache_res
        if filters and "keyword" in filters:
            discussions = GroupDiscussion.query.filter(
                GroupDiscussion.title.like(f"%{filters.get('keyword')}%") |
                GroupDiscussion.content.like(f"%{filters.get('keyword')}%")
            )
        else:
            discussions = GroupDiscussion.query.filter_by(**filters) if filters else GroupDiscussion.query
        if limit == 1:
            discussion = discussions.first()
            res = extractGroupDiscussion(discussion) if discussion else None
        elif limit > 1:
            discussions = discussions.limit(limit).all()
            res = [extractGroupDiscussion(discussion) for discussion in discussions]
        else:
            discussions = discussions.all()
            res = [extractGroupDiscussion(discussion) for discussion in discussions]
        self.cache.setGroupDiscussion(res)
        return res

    def getGroupDiscussionNum(self, **filters) -> int:
        """
        获取圈子内帖子数量
        :param filters: 用于筛选的参数，包括GroupDiscussion的全部字段，至少需要包含"group_id"
        :return: 帖子数量
        """
        if "group_id" in filters:
            res = self.cache.getGroupDiscussion(group_id=filters.get("group_id"))
            if res:
                return len(res)
        return GroupDiscussion.query.filter_by(**filters).count()

    def markGroupDiscussionsAsRead(self, *groups_id) -> bool:
        """
        将Group的所有Journals都标记为已读
        :param groups_id: Group的id，可以传入多个
        :return: 是否成功标记
        """
        if not groups_id:
            return False
        for group_id in groups_id:
            GroupDiscussion.query.filter_by(group_id=group_id).update({"is_read": True})
            self.cache.markGroupDiscussionsAsRead(group_id)
        db.session.commit()
        return True

    def deleteGroupDiscussion(self, discuss_id: int) -> bool:
        """
        根据discuss_id，删除帖子
        :param discuss_id: 帖子id
        :return: 是否成功删除
        """
        discussion = GroupDiscussion.query.filter_by(id=discuss_id).first()
        if not discussion:
            return False
        db.session.delete(discussion)
        db.session.commit()
        self.cache.deleteGroupDiscussion(discuss_id)
        return True

    """GroupDiscussionReply相关"""

    @staticmethod
    def addGroupDiscussionReply(
            author_id: int, discussion_id: int, content: str, reply_time: Union[str, datetime] = None
    ) -> bool:
        """
        为某个GroupDiscussion添加回复
        :param author_id: 回复者id
        :param discussion_id: 帖子id
        :param content: 回复内容
        :param reply_time: 回复时间
        :return: 是否成功添加回复
        """
        if not reply_time:
            reply_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(reply_time, datetime):
            reply_time = reply_time.strftime("%Y-%m-%d %H:%M:%S")
        reply = GroupDiscussionReply(
            author_id=author_id,
            discussion_id=discussion_id,
            reply_time=reply_time,
            content=content
        )
        if author_id == GroupDiscussion.query.filter_by(id=discussion_id).first().poster_id:
            reply.is_read = True  # 如果是帖子作者回复，自动标记为已读
        db.session.add(reply)
        db.session.commit()
        return True

    @staticmethod
    def getGroupDiscussionReplies(
            limit: int = 1, **filters
    ) -> Union[list[GroupDiscussionReplyDict], GroupDiscussionReplyDict, list[None], None]:
        """
        获取帖子回复
        :param limit: 限制返回的数量，默认为1即返回单个回复信息，其他正值为限制量，0、负值、None为不限制
        :param filters: 用于筛选的参数，包括GroupDiscussionReply的全部字段和"keyword"字段(用于模糊搜索)
        :return: 回复信息(GroupDiscussionReplyDict或list[GroupDiscussionReplyDict])
        """
        if filters and "keyword" in filters:
            replies = GroupDiscussionReply.query.filter(
                GroupDiscussionReply.content.like(f"%{filters.get('keyword')}%")
            )
        else:
            replies = GroupDiscussionReply.query.filter_by(**filters) if filters else GroupDiscussionReply.query
        if limit == 1:
            reply = replies.first()
            return extractGroupDiscussionReply(reply) if reply else None
        elif limit > 1:
            replies = replies.limit(limit).all()
            return [extractGroupDiscussionReply(reply) for reply in replies]
        else:
            replies = replies.all()
            return [extractGroupDiscussionReply(reply) for reply in replies]

    @staticmethod
    def getGroupReply(group_id: int, limit=5) -> list[dict]:
        """
        按照时间降序获取圈子内所有回复
        :param group_id: 圈子id
        :param limit: 限制返回的数量，默认为最新的5条
        :return:
        """
        discussion_id = [discussion.id for discussion in GroupDiscussion.query.filter_by(group_id=group_id).all()]
        replies = GroupDiscussionReply.query.filter(GroupDiscussionReply.discussion_id.in_(discussion_id)).order_by(
            GroupDiscussionReply.reply_time.desc()).limit(limit).all()
        return [extractGroupDiscussionReply(reply) for reply in replies]

    @staticmethod
    def getGroupDiscussionReplyNum(**filters) -> int:
        """
        获取某个帖子的回复数量
        :param filters: 用于筛选的参数，包括GroupDiscussionReply的全部字段，至少需要包含"discussion_id"
        :return: 回复数量
        """
        return GroupDiscussionReply.query.filter_by(**filters).count()

    @staticmethod
    def markDiscussionRepliesAsRead(*discussions_id) -> bool:
        """
        将GroupDiscussion的所有Replies都标记为已读
        :param discussions_id: GroupDiscussion的id，可以传入多个
        :return: 是否成功标记
        """
        if not discussions_id:
            return False
        for discussion_id in discussions_id:
            GroupDiscussionReply.query.filter_by(discussion_id=discussion_id).update({"is_read": True})
        db.session.commit()
        return True

    """GroupUser相关"""

    def addGroupUser(self, user_id: int, group_id: int, join_time: Union[str, datetime] = None) -> bool:
        """
        添加圈子成员
        :param user_id: 用户id
        :param group_id: 圈子id
        :param join_time: 加入时间
        :return: 是否成功添加圈子成员
        """
        if not join_time:
            join_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(join_time, datetime):
            join_time = join_time.strftime("%Y-%m-%d %H:%M:%S")
        user = GroupUser(
            user_id=user_id,
            group_id=group_id,
            join_time=join_time
        )
        db.session.add(user)
        db.session.commit()
        self.cache.setGroupUser(extractGroupUser(user))
        return True

    def deleteGroupUser(self, group_id: int, user_id: int) -> bool:
        """
        删除圈子成员
        :param group_id: 圈子id
        :param user_id: 用户id
        :return: 是否成功删除圈子成员
        """
        user = GroupUser.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not user:
            return False
        db.session.delete(user)
        db.session.commit()
        self.cache.deleteGroupUser(group_id, user_id)
        return True

    def getGroupUser(self, limit: int = 1, **filters) -> Union[list[GroupUserDict], GroupUserDict, list[None], None]:
        """
        获取圈子成员信息
        :param limit: 限制返回的数量，默认为1即返回单个成员信息，其他正值为限制量，0、负值、None为不限制
        :param filters: 用于筛选的参数，包括GroupUser的全部字段
        :return: 成员信息(GroupUserDict或list[GroupUserDict])
        """
        if "group_id" in filters and limit == 0:  # 通过group_id获取全部成员
            cache_res = self.cache.getGroupUser(filters["group_id"])
            if cache_res:
                return cache_res
        users = GroupUser.query.filter_by(**filters) if filters else GroupUser.query
        if limit == 1:
            user = users.first()
            res = extractGroupUser(user) if user else None
        elif limit > 1:
            users = users.limit(limit).all()
            res = [extractGroupUser(user) for user in users]
        else:
            users = users.all()
            res = [extractGroupUser(user) for user in users]
        self.cache.setGroupUser(res)
        return res

    def getGroupUsersNum(self, group_id: int) -> int:
        """
        获取圈子成员数量
        :param group_id: 圈子id
        :return: 成员数量
        """
        cache_res = self.cache.getGroupUser(group_id)
        if cache_res:
            return len(cache_res)
        return GroupUser.query.filter_by(group_id=group_id).count()

    """Chat相关"""

    def addChat(self, sender_id: int, receiver_id: int, send_time: Union[datetime, str], content: str) -> bool:
        """
        添加聊天信息
        :param sender_id: 发送者id
        :param receiver_id: 接收者id
        :param send_time: 发送时间
        :param content: 聊天内容
        :return: 是否成功添加聊天信息
        """
        if isinstance(send_time, datetime):
            send_time = send_time.strftime("%Y-%m-%d %H:%M:%S")
        chat = Chat(sender_id=sender_id, receiver_id=receiver_id, send_time=send_time, content=content)
        db.session.add(chat)
        db.session.commit()
        chat_dict = extractChat(
            Chat.query.filter_by(sender_id=sender_id, receiver_id=receiver_id, send_time=send_time).first()
        )
        self.cache.setChat(chat_dict)
        return True

    def getChat(self, sender_id: int, receiver_id: int, each=False, limit=0) -> Union[
        list[ChatDict], ChatDict, list[None], None
    ]:
        """
        获取聊天信息
        :param sender_id: sender_id字段
        :param receiver_id: receiver_id字段
        :param each: 是否包含交换sender_id和receiver_id后的结果(默认为False)
        :param limit: 限制返回的数量，默认为0即不限制，其他正值为限制数量
        :return: 聊天信息(ChatDict或list[ChatDict])
        """
        cache_res = self.cache.getChat(sender_id, receiver_id, each, limit)
        if cache_res:
            return cache_res
        if each:
            chats = Chat.query.filter(
                or_(
                    (Chat.sender_id == sender_id) & (Chat.receiver_id == receiver_id),
                    (Chat.sender_id == receiver_id) & (Chat.receiver_id == sender_id)
                )
            )
        else:
            chats = Chat.query.filter_by(sender_id=sender_id, receiver_id=receiver_id)
        chats = chats.order_by(Chat.send_time.asc())
        if limit == 1:
            chat = chats.first()
            res = extractChat(chat) if chat else None
        elif limit > 1:
            chats = chats.limit(limit).all()
            res = [extractChat(chat) for chat in chats]
        else:
            chats = chats.all()
            res = [extractChat(chat) for chat in chats]
        self.cache.setChat(res)
        return res

    @staticmethod
    def getChatNum(sender_id: int, receiver_id: int, each=False) -> int:
        """
        获取两人之间的聊天数量
        :param sender_id: sender_id字段
        :param receiver_id: receiver_id字段
        :param each: 是否包含交换sender_id和receiver_id后的结果(默认为False)
        :return: 聊天数量
        """
        if each:
            return (Chat.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).count() +
                    Chat.query.filter_by(sender_id=receiver_id, receiver_id=sender_id).count())
        return Chat.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).count()

    @staticmethod
    def getChatLastTime(sender_id, receiver_id, each=False) -> str:
        """
        获取两人之间最后的聊天时间
        :param sender_id: sender_id字段
        :param receiver_id: receiver_id字段
        :param each: 是否包含交换sender_id和receiver_id后的结果(默认为False)
        :return: 最后的聊天时间(%Y-%m-%d %H:%M:%S格式的字符串)
        """
        if not each:
            chat = Chat.query.filter_by(
                sender_id=sender_id, receiver_id=receiver_id
            ).order_by(Chat.send_time.desc()).first()
        else:
            chat1 = Chat.query.filter_by(
                sender_id=sender_id, receiver_id=receiver_id
            ).order_by(Chat.send_time.desc()).first()
            chat2 = Chat.query.filter_by(
                sender_id=receiver_id, receiver_id=sender_id
            ).order_by(Chat.send_time.desc()).first()
            if not (chat1 and chat2):
                chat = chat2 if chat2 else chat1
            else:
                chat = chat1 if chat1.send_time > chat2.send_time else chat2
        return chat.send_time if chat else None

    def markChatsAsRead(self, receiver_id: int, *sender_ids):
        """
        将Chat的所有信息都标记为已读
        :param receiver_id: receiver_id字段
        :param sender_ids: sender_id字段，可以传入多个
        :return: 是否成功标记
        """
        if not sender_ids:
            return False
        for sender_id in sender_ids:
            Chat.query.filter_by(receiver_id=receiver_id, sender_id=sender_id).update({"is_read": True})
        db.session.commit()
        for sender_id in sender_ids:
            self.cache.markChatAsRead(sender_id, receiver_id)
        return True

    """错误响应相关"""

    def getError(self, error_code: int) -> ErrorDict:
        """
        根据errorCode获取错误信息
        :param error_code: 错误码
        :return: 错误信息
        """
        cache_res = self.cache.getError(error_code)
        if cache_res:
            return cache_res
        error = Error.query.filter_by(error_code=error_code).first()
        error_dict = extractError(error)
        self.cache.setError(error_dict)
        return error_dict

    """消息相关"""

    def getAllUnreadMessage(self, user_id: int) -> UnreadMessagesDict:
        """
        获取用户的所有未读消息(各类消息，包括书评回复、帖子回复、新私信、圈子新帖)
        :param user_id: 用户id，获取该用户的全部未读信息
        :return: 未读消息字典，UnreadMessagesDict类型
        """
        # 书评回复
        journals = self.getJournal(limit=0, author_id=user_id)
        journal_comments: list[dict] = [
            extractJournalComment(comment) for comment in JournalComment.query.filter(
                JournalComment.journal_id.in_([journal.get("id") for journal in journals]),
                JournalComment.is_read == False  # 若此处提示 PEP 8: E712相关警告请忽略，必须这么写才能被SQLAlchemy识别为SQL判断条件
            ).order_by(JournalComment.publish_time.desc()).all()
        ]
        for comment in journal_comments:
            comment["account"] = self.getUser(id=comment.get("author_id")).get("account")

        # 圈子新帖(先找到该用户创建的圈子，再找到该圈子的所有未读帖子)
        group_ids = [group.id for group in Group.query.filter_by(founder_id=user_id).all()]
        group_discussions: list[dict] = [
            extractGroupDiscussion(discussion)
            for discussion in GroupDiscussion.query.filter(
                GroupDiscussion.group_id.in_(group_ids),
                GroupDiscussion.is_read == False  # 若此处提示 PEP 8: E712相关警告请忽略，必须这么写才能被SQLAlchemy识别为SQL判断条件
            ).order_by(GroupDiscussion.post_time.desc()).all()
        ]
        for discussion in group_discussions:
            discussion["account"] = self.getUser(id=discussion.get("poster_id")).get("account")

        # 帖子回复(先找到该用户发表的帖子，再找到该帖子的所有未读回复)
        discussion_ids = [item.id for item in GroupDiscussion.query.filter_by(poster_id=user_id).all()]
        discussion_replies: list[dict] = [
            extractGroupDiscussionReply(reply)
            for reply in GroupDiscussionReply.query.filter(
                GroupDiscussionReply.discussion_id.in_(discussion_ids),
                GroupDiscussionReply.is_read == False  # 若此处提示 PEP 8: E712相关警告请忽略，必须这么写才能被SQLAlchemy识别为SQL判断条件
            ).order_by(GroupDiscussionReply.reply_time.desc()).all()
        ]
        for reply in discussion_replies:
            reply["account"] = self.getUser(id=reply.get("author_id")).get("account")

        # 私信
        chats: list[dict] = [
            extractChat(chat)
            for chat in Chat.query.filter_by(receiver_id=user_id, is_read=False).order_by(Chat.send_time.asc()).all()
        ]
        for chat in chats:
            chat["account"] = self.getUser(id=chat.get("sender_id")).get("account")

        return UnreadMessagesDict(
            journal_comments=journal_comments,
            group_discussions=group_discussions,
            discussion_replies=discussion_replies,
            chats=chats
        )

    @staticmethod
    def getAllUnreadMessageNum(user_id: int) -> dict[str, int]:
        """
        获取用户的所有未读消息数量(各类消息，包括书评回复、帖子回复、新私信、圈子新帖)
        :param user_id: 用户id
        :return: 未读消息数量字典
        """
        # 书评回复
        journal_comments_num = JournalComment.query.filter_by(author_id=user_id, is_read=False).count()
        # 圈子新帖
        group_id = [item.id for item in Group.query.filter_by(founder_id=user_id).all()]
        group_discussions_num = GroupDiscussion.query.filter(
            GroupDiscussion.group_id.in_(group_id),
            GroupDiscussion.is_read == False  # 若此处提示 PEP 8: E712相关警告请忽略，必须这么写才能被SQLAlchemy识别为SQL判断条件
        ).count()
        # 帖子回复
        discussion_id = [item.id for item in GroupDiscussion.query.filter_by(poster_id=user_id).all()]
        discussion_replies_num = GroupDiscussionReply.query.filter(
            GroupDiscussionReply.discussion_id.in_(discussion_id),
            GroupDiscussionReply.is_read == False  # 若此处提示 PEP 8: E712相关警告请忽略，必须这么写才能被SQLAlchemy识别为SQL判断条件
        ).count()
        # 私信
        chats_num = Chat.query.filter_by(receiver_id=user_id, is_read=False).count()
        return {"journalComment": journal_comments_num,
                "groupDiscussion": group_discussions_num,
                "discussionReply": discussion_replies_num,
                "chat": chats_num}
