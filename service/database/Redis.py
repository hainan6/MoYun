"""Redis缓存相关"""
import traceback
from datetime import datetime
from typing import Union

import redis
from werkzeug.security import generate_password_hash

from service.database.Utils import BookDict, UserDict, JournalDict, JournalCommentDict, JournalLikeDict, \
    GroupDict, GroupDiscussionDict, GroupUserDict, ChatDict, ErrorDict


class Cache:
    """
    使用Redis作为数据库(MySQL)的缓存
    """

    def __init__(self, host, port, database, password=None):
        if password:
            self.host = redis.StrictRedis(host=host, port=port, db=database, password=password)
        else:
            self.host = redis.StrictRedis(host=host, port=port, db=database)

    def _set(self, key: str, value: Union[int, str, bool], expire: int = None) -> bool:
        """
        存储基本数据类型：int, str, bool
        :param key: 键
        :param value: 值
        :return: 是否存储成功
        """
        if value is None:
            value = ""
        self.host.set(key, value)
        if expire:
            self.host.expire(key, expire)
        return True

    def _get(self, key: str, type_: Union[str, int, float] = str) -> Union[str, int, float, None]:
        """
        读取基本数据类型
        :param key: 键
        :param type_: 指定返回类型，未指定则返回str或None，指定则尝试转换为指定类型，失败则返回None
        """
        res = self.host.get(key)
        if res:
            res = res.decode()
        else:
            return None

        if type_ == str:
            return res
        elif type_ == int:
            return int(res)
        elif type_ == float:
            return float(res)
        else:
            return None

    def _setList(self, key: str, value: list, expire: int = 600) -> bool:
        """
        存储列表
        :param key: 键
        :param value: 值
        :param expire: 过期时间，默认为10分钟，list类元素的过期时间应当早于hash类元素的过期时间，以避免出现索引仍存在但实体已过期的情况
        """
        try:
            self.host.delete(key)  # 先删除已有的list
            value.reverse()  # 反转list，以便于正向地存储
            value = [item if item is not None else "" for item in value]
            self.host.lpush(key, *value)  # 再插入新的list
            self.host.expire(key, expire)
            return True
        except:
            traceback.print_exc()
            return False

    def _appendList(self, key: str, value: Union[int, str], expire: int = 600) -> bool:
        """
        追加列表
        :param key: 键
        :param value: 值
        :param expire: 过期时间，默认为10分钟，list类元素的过期时间应当早于hash类元素的过期时间，以避免出现索引仍存在但实体已过期的情况
        """
        try:
            self.host.lpush(key, value)
            self.host.expire(key, expire)
            return True
        except:
            return False

    def _getList(self, key: str) -> Union[list[str], None]:
        """
        读取列表
        :param key: 键
        """
        res = self.host.lrange(key, 0, -1)
        if res:
            res = [item.decode() for item in res]
            return res
        else:
            return None

    def _setDict(self, key: str, value: dict, expire: int = 1200) -> bool:
        """
        存储字典
        :param key: 键
        :param value: 值
        """
        try:
            self.host.delete(key)  # 先删除已有的dict
            for k, v in value.items():
                if v is None:
                    v = ""
                if isinstance(v, datetime):
                    v = v.strftime("%Y-%m-%d %H:%M:%S")
                self.host.hset(key, k, v)
            else:
                self.host.expire(key, expire)
                return True
        except:
            return False

    def _modifyDict(self, key: str, field: str, value: Union[int, float, str], expire: int = 1200) -> bool:
        """
        修改字典中的某个值
        :param key: 键
        :param field: 字段
        :param value: 值
        """
        try:
            if value is None:
                value = ""
            self.host.hset(key, field, value)
            self.host.expire(key, expire)
            return True
        except:
            return False

    def _getDict(self, key: str) -> Union[dict[str, str], None]:
        """
        读取字典
        :param key: 键
        """
        res = self.host.hgetall(key)
        if res:
            return {k.decode(): v.decode() for k, v in res.items()}
        else:
            return None

    def _getDictField(self, key: str, field: str, type_: Union[str, int, float] = str) -> Union[str, int, float, None]:
        """
        读取字典中的字段
        """
        res = self.host.hget(key, field)
        if res:
            res = res.decode()
        else:
            return None

        if type_ == str:
            return res
        elif type_ == int:
            return int(res)
        elif type_ == float:
            return float(res)
        else:
            return None

    """User相关"""

    def setUser(self, user: Union[UserDict, list[UserDict]]):
        """
        存储用户信息
        :param user: 用户信息
        """
        if not user:
            return
        if isinstance(user, list):
            for u in user:
                self._setDict(f"User_{u.get('id')}", u)
        else:
            self._setDict(f"User_{user.get('id')}", user)

    def modifyUser(self, user_id: Union[int, str], **kwargs):
        """
        修改用户信息
        :param user_id: 用户id
        :param kwargs: 修改的字段
        """
        user = self.getUser(user_id)
        for k, v in kwargs.items():
            if k != "password":
                user[k] = v
            else:
                user[k] = generate_password_hash(v)
        self.setUser(user)

    def getUser(self, user_id: Union[int, str], with_password=False) -> Union[UserDict, None]:
        """
        获取用户信息
        :param user_id: 用户id
        :param with_password: 是否返回密码
        """
        user = self._getDict(f"User_{user_id}")
        if user:
            user['id'] = int(user['id'])
            if not with_password:
                user["password"] = None
            return UserDict(**user)
        return None

    """Journal相关"""

    def setJournal(self, journal: Union[JournalDict, list[JournalDict]]):
        """
        存储日志
        :param journal: 日志信息
        """
        if isinstance(journal, list):
            for j in journal:
                j_copy = j.copy()
                j_copy['content'] = "\n".join(j['content'])
                self._setDict(f"Journal_{j_copy.get('id')}", j_copy)
        elif isinstance(journal, dict):
            journal_copy = journal.copy()
            journal_copy['content'] = "\n".join(journal['content'])
            self._setDict(f"Journal_{journal_copy.get('id')}", journal_copy)
        else:
            return

    def getJournal(self, journal_id: Union[int, str]):
        """
        获取日志
        :param journal_id: 日志id
        """
        journal = self._getDict(f"Journal_{journal_id}")
        if journal:
            journal['id'] = int(journal['id'])
            journal['content'] = journal['content'].split("\n")
            journal['like_num'] = int(journal['like_num'])
            journal['comment_num'] = int(journal['comment_num'])
            return JournalDict(**journal)
        return None

    """JournalComment相关"""

    def setJournalComment(self, comment: Union[JournalCommentDict, list[JournalCommentDict]]):
        """
        存储日志评论
        :param comment: 日志评论信息
        """
        if isinstance(comment, list):  # 如果传入的是列表
            journal_comment_ids = self._getList(f"Journal_{comment[0].get('journal_id')}_comment_ids")  # 获取该书评的评论id列表
            if not journal_comment_ids:
                journal_comment_ids = []
            for c in comment:
                c_copy = c.copy()
                if str(c_copy.get('id')) not in journal_comment_ids:
                    self._appendList(f"Journal_{c_copy.get('journal_id')}_comment_ids", c_copy.get('id'))
                c_copy['is_read'] = 1 if c_copy['is_read'] else 0
                self._setDict(f"JournalComment_{c_copy.get('id')}", c_copy)
        elif isinstance(comment, dict):  # 如果传入的是单个对象
            journal_comment_ids = self._getList(f"Journal_{comment.get('journal_id')}_comment_ids")
            if not journal_comment_ids:
                journal_comment_ids = []
            comment_copy = comment.copy()
            if str(comment_copy.get('id')) not in journal_comment_ids:
                self._appendList(f"Journal_{comment_copy.get('journal_id')}_comment_ids", comment_copy.get('id'))
            comment_copy['is_read'] = 1 if comment_copy['is_read'] else 0
            self._setDict(f"JournalComment_{comment_copy.get('id')}", comment_copy)
        else:
            return

    def markJournalCommentsAsRead(self, journal_id: Union[int, str]):
        """
        将journal_id对应的所有评论标记为已读
        :param journal_id: 日志id
        """
        comment_ids = self._getList(f"Journal_{journal_id}_comment_ids")
        if not comment_ids:
            return
        for comment_id in comment_ids:
            comment = self._getDict(f"JournalComment_{comment_id}")
            comment['is_read'] = 1
            self._setDict(f"JournalComment_{comment_id}", comment)

    def getJournalComment(self, journal_id: Union[int, str]) -> Union[list[JournalCommentDict], None]:
        """
        获取journal_id对应的所有评论
        :param journal_id: 日志id
        """
        comment_ids = self._getList(f"Journal_{journal_id}_comment_ids")
        comments = []
        if not comment_ids:
            return None
        for comment_id in comment_ids:
            comment = self._getDict(f"JournalComment_{comment_id}")
            comment['id'] = int(comment['id'])
            comment['journal_id'] = int(comment['journal_id'])
            comment['author_id'] = int(comment['author_id'])
            comment['is_read'] = comment['is_read'] != '0'
            comments.append(JournalCommentDict(**comment))
        return comments

    """JournalLike相关"""

    def setJournalLike(self, like: Union[JournalLikeDict, list[JournalLikeDict]]):
        """
        存储日志点赞
        :param like: 日志点赞信息
        """
        if isinstance(like, list):
            like_author_ids = self._getList(f"Journal_{like[0].get('journal_id')}_like_author_ids")
            if not like_author_ids:
                like_author_ids = []
            for l in like:
                if str(l.get('author_id')) not in like_author_ids:
                    self._appendList(f"Journal_{l.get('journal_id')}_like_author_ids", l.get('author_id'))
                self._setDict(f"JournalLike_{l.get('author_id')}", l)
        elif isinstance(like, dict):
            like_author_ids = self._getList(f"Journal_{like.get('journal_id')}_like_author_ids")
            if not like_author_ids:
                like_author_ids = []
            if str(like.get('author_id')) not in like_author_ids:
                self._appendList(f"Journal_{like.get('journal_id')}_like_author_ids", like.get('author_id'))
            self._setDict(f"JournalLike_{like.get('author_id')}", like)
        else:
            return

    def getJournalLike(self, journal_id: Union[int, str]) -> Union[list[JournalLikeDict], None]:
        """
        获取journal_id对应的所有点赞
        :param journal_id: 日志id
        """
        like_author_ids = self._getList(f"Journal_{journal_id}_like_author_ids")
        likes = []
        if not like_author_ids:
            return None
        for author_id in like_author_ids:
            like = self._getDict(f"JournalLike_{author_id}")
            like['author_id'] = int(like['author_id'])
            like['journal_id'] = int(like['journal_id'])
            likes.append(JournalLikeDict(**like))
        return likes

    """Book相关"""

    def setBook(self, book: Union[BookDict, list[BookDict]]):
        """
        存储书籍信息
        :param book: 书籍信息
        """
        if isinstance(book, list):
            for b in book:
                self._setDict(f"Book_{b.get('id')}", b)
        elif isinstance(book, dict):
            self._setDict(f"Book_{book.get('id')}", book)
        else:
            return

    def modifyBook(self, book_id: Union[int, str], **kwargs):
        """
        修改书籍信息
        :param book_id: 书籍id
        :param kwargs: 修改的字段
        """
        kwargs_copy = kwargs.copy()
        book = self.getBook(book_id)
        for k, v in kwargs_copy.items():
            if v is None:
                v = ""
            book[k] = v
        self.setBook(book)

    def getBook(self, book_id: Union[int, str]) -> Union[BookDict, None]:
        """
        获取书籍信息
        :param book_id: 书籍id
        """
        book = self._getDict(f"Book_{book_id}")
        if book:
            book['id'] = int(book['id'])
            book['page'] = int(book['page']) if book['page'] else ""
            book['douban_score'] = float(book['douban_score']) if book['douban_score'] else ""
            book['bangumi_score'] = float(book['bangumi_score']) if book['bangumi_score'] else ""
            return BookDict(**book)
        return None

    """Group相关"""

    def setGroup(self, group: Union[GroupDict, list[GroupDict]]):
        """
        存储群组信息
        :param group: 群组信息
        """
        if isinstance(group, list):
            for g in group:
                self._setDict(f"Group_{g.get('id')}", g)
        elif isinstance(group, dict):
            self._setDict(f"Group_{group.get('id')}", group)
        else:
            return

    def modifyGroup(self, group_id: Union[int, str], **kwargs):
        """
        修改群组信息
        :param group_id: 群组id
        :param kwargs: 修改的字段
        """
        group = self.getGroup(group_id)
        kwargs_copy = kwargs.copy()
        for k, v in kwargs_copy.items():
            group[k] = v
        self.setGroup(group)

    def getGroup(self, group_id: Union[int, str]) -> Union[GroupDict, None]:
        """
        获取群组信息
        :param group_id: 群组id
        """
        group = self._getDict(f"Group_{group_id}")
        if group:
            group['id'] = int(group['id'])
            group['founder_id'] = int(group['founder_id'])
            return GroupDict(**group)
        return None

    """GroupDiscussion相关"""

    def setGroupDiscussion(self, discussion: Union[GroupDiscussionDict, list[GroupDiscussionDict]]):
        """
        存储GroupDiscussion
        :param discussion: 讨论信息
        """
        if not discussion:
            return
        if isinstance(discussion, list):
            group_discussion_ids = self._getList(f"Group_{discussion[0].get('group_id')}_discussion_ids")
            if not group_discussion_ids:
                group_discussion_ids = []
            for d in discussion:
                d_copy = d.copy()
                if str(d_copy.get('id')) not in group_discussion_ids:
                    self._appendList(f"Group_{d_copy.get('group_id')}_discussion_ids", d_copy.get('id'))
                d_copy['is_read'] = 1 if d_copy['is_read'] else 0
                self._setDict(f"GroupDiscussion_{d_copy.get('id')}", d_copy)
        elif isinstance(discussion, dict):
            group_discussion_ids = self._getList(f"Group_{discussion.get('group_id')}_discussion_ids")
            if not group_discussion_ids:
                group_discussion_ids = []
            discussion_copy = discussion.copy()
            if str(discussion_copy.get('id')) not in group_discussion_ids:
                self._appendList(f"Group_{discussion_copy.get('group_id')}_discussion_ids", discussion_copy.get('id'))
            discussion_copy['is_read'] = 1 if discussion_copy['is_read'] else 0
            self._setDict(f"GroupDiscussion_{discussion_copy.get('id')}", discussion_copy)
        else:
            return

    def markGroupDiscussionsAsRead(self, group_id: Union[int, str]):
        """
        将group_id对应的所有discussion标记为已读
        :param group_id: 群组id
        """
        discussion_ids = self._getList(f"Group_{group_id}_discussion_ids")
        if not discussion_ids:
            return
        for discussion_id in discussion_ids:
            discussion = self._getDict(f"GroupDiscussion_{discussion_id}")
            discussion['is_read'] = 1
            self._setDict(f"GroupDiscussion_{discussion_id}", discussion)

    def deleteGroupDiscussion(self, discussion_id: Union[int, str]):
        """
        删除discussion_id对应的discussion
        :param discussion_id: 讨论id
        """
        discussion = self._getDict(f"GroupDiscussion_{discussion_id}")
        group_discussion_ids = self._getList(f"Group_{discussion.get('group_id')}_discussion_ids")
        group_discussion_ids.remove(str(discussion_id))
        self._setList(f"Group_{discussion.get('group_id')}_discussion_ids", group_discussion_ids)
        self.host.delete(f"GroupDiscussion_{discussion_id}")

    def getGroupDiscussion(self, group_id: Union[int, str] = None, discussion_id: Union[int, str] = None) -> Union[
        list[GroupDiscussionDict], GroupDiscussionDict, None
    ]:
        """
        获取GroupDiscussion
        :param group_id: 群组id
        :param discussion_id: 讨论id
        """
        if group_id:  # 指定了group_id，则根据Group_{group_id}_discussion_ids找到全部discussion，并返回
            discussion_ids = self._getList(f"Group_{group_id}_discussion_ids")
            discussions = []
            if not discussion_ids:
                return None
            for discussion_id in discussion_ids:
                discussion = self._getDict(f"GroupDiscussion_{discussion_id}")
                discussion['id'] = int(discussion['id'])
                discussion['poster_id'] = int(discussion['poster_id'])
                discussion['group_id'] = int(discussion['group_id'])
                discussion['is_read'] = discussion['is_read'] != '0'
                discussions.append(GroupDiscussionDict(**discussion))
            return discussions
        elif discussion_id:  # 指定了discussion_id，则返回该discussion
            discussion = self._getDict(f"GroupDiscussion_{discussion_id}")
            if discussion:
                discussion['id'] = int(discussion['id'])
                discussion['poster_id'] = int(discussion['poster_id'])
                discussion['group_id'] = int(discussion['group_id'])
                discussion['is_read'] = discussion['is_read'] != '0'
                return GroupDiscussionDict(**discussion)
            return None
        else:  # 未指定参数，则返回None
            return None

    """GroupUser相关"""

    def setGroupUser(self, user: Union[GroupUserDict, list[GroupUserDict]]):
        """
        存储group_id中的用户
        :param user: 用户信息
        """
        if isinstance(user, list):
            for u in user:
                self._setDict(f"Group_{u.get('group_id')}_User_{u.get('user_id')}", u)
                group_user_ids = self._getList(f"Group_{u.get('group_id')}_user_ids")
                if not group_user_ids:
                    group_user_ids = []
                group_user_ids.append(str(u.get('user_id')))
                self._setList(f"Group_{u.get('group_id')}_user_ids", group_user_ids)
        elif isinstance(user, dict):
            self._setDict(f"Group_{user.get('group_id')}_User_{user.get('user_id')}", user)
            group_user_ids = self._getList(f"Group_{user.get('group_id')}_user_ids")
            if not group_user_ids:
                group_user_ids = []
            group_user_ids.append(str(user.get('user_id')))
            self._setList(f"Group_{user.get('group_id')}_user_ids", group_user_ids)
        else:
            return

    def deleteGroupUser(self, group_id: Union[int, str], user_id: Union[int, str]):
        """
        删除group_id中user_id对应的用户
        :param group_id: 群组id
        :param user_id: 用户id
        """
        self.host.delete(f"Group_{group_id}_User_{user_id}")
        group_user_ids = self._getList(f"Group_{group_id}_user_ids")
        group_user_ids.remove(str(user_id))
        self._setList(f"Group_{group_id}_user_ids", group_user_ids)

    def getGroupUser(self, group_id: Union[int, str]) -> Union[list[GroupUserDict], None]:
        """
        获取group_id对应的所有用户
        :param group_id: 群组id
        """
        user_ids = self._getList(f"Group_{group_id}_user_ids")
        if not user_ids:
            return None
        users = []
        for user_id in user_ids:
            user = self._getDict(f"Group_{group_id}_User_{user_id}")
            if user:
                user['user_id'] = int(user['user_id'])
                user['group_id'] = int(user['group_id'])
                users.append(GroupUserDict(**user))
        return users

    """Chat相关"""

    def setChat(self, chat: Union[ChatDict, list[ChatDict]]):
        """
        存储chat
        :param chat: chat信息
        """
        if not chat:
            return
        if isinstance(chat, list):
            chat_ids = self._getList(
                f"Chat_{chat[0].get('sender_id')}_{chat[0].get('receiver_id')}_ids"
            )  # 记录sender和receiver的所有chat的id
            if not chat_ids:
                chat_ids = []
            for c in chat:
                c_copy = c.copy()
                if str(c_copy.get('id')) not in chat_ids:
                    self._appendList(
                        f"Chat_{c_copy.get('sender_id')}_{c_copy.get('receiver_id')}_ids", c_copy.get('id')
                    )
                c_copy['is_read'] = 1 if c_copy['is_read'] else 0
                self._setDict(f"Chat_{c_copy.get('id')}", c_copy)
        elif isinstance(chat, dict):
            chat_ids = self._getList(
                f"Chat_{chat.get('sender_id')}_{chat.get('receiver_id')}_ids"
            )
            if not chat_ids:
                chat_ids = []
            chat_copy = chat.copy()
            if str(chat_copy.get('id')) not in chat_ids:
                self._appendList(
                    f"Chat_{chat_copy.get('sender_id')}_{chat_copy.get('receiver_id')}_ids", chat_copy.get('id')
                )
            chat_copy['is_read'] = 1 if chat_copy['is_read'] else 0
            self._setDict(f"Chat_{chat_copy.get('id')}", chat_copy)
        else:
            return

    def markChatAsRead(self, sender_id: Union[int, str], receiver_id: Union[int, str]):
        """
        将sender和receiver之间的所有chat标记为已读
        :param sender_id: 发送者id
        :param receiver_id: 接收者id
        """
        chat_ids = self._getList(f"Chat_{sender_id}_{receiver_id}_ids")
        if not chat_ids:
            return
        for chat_id in chat_ids:
            chat = self._getDict(f"Chat_{chat_id}")
            chat['is_read'] = 1
            self._setDict(f"Chat_{chat_id}", chat)

    def getChat(self, sender_id: int, receiver_id: int, each: bool, limit: int) -> list[Union[ChatDict, None]]:
        """
        获取sender和receiver之间的chat
        :param sender_id: 发送者id
        :param receiver_id: 接收者id
        :param each: 是否返回sender和receiver之间的所有chat
        :param limit: 返回的chat数量
        """
        if each:
            chat_ids_1 = self._getList(f"Chat_{sender_id}_{receiver_id}_ids")
            chat_ids_2 = self._getList(f"Chat_{receiver_id}_{sender_id}_ids")
            chat_ids_1 = chat_ids_1 if chat_ids_1 else []
            chat_ids_2 = chat_ids_2 if chat_ids_2 else []
            chat_ids = chat_ids_1 + chat_ids_2
        else:
            chat_ids = self._getList(f"Chat_{sender_id}_{receiver_id}_ids")
        chat_ids.sort(key=lambda x: int(x))
        chats = []
        if not chat_ids:
            return []
        for chat_id in chat_ids:
            chat = self._getDict(f"Chat_{chat_id}")
            chat['id'] = int(chat['id'])
            chat['sender_id'] = int(chat['sender_id'])
            chat['receiver_id'] = int(chat['receiver_id'])
            chat['is_read'] = chat['is_read'] != '0'
            chats.append(ChatDict(**chat))
        if limit != 0:
            return chats[-limit:]
        return chats

    """Error相关"""

    def setError(self, error: Union[ErrorDict, list[ErrorDict]]):
        """
        存储错误信息
        :param error: 错误信息
        """
        if not error:
            return
        if isinstance(error, dict):
            self._setDict(f"Error_{error.get('error_code')}", error)
        elif isinstance(error, list):
            for e in error:
                self._setDict(f"Error_{e.get('error_code')}", e)
        else:
            return

    def getError(self, error_code: Union[int, str]):
        """
        获取错误信息
        :param error_code: 错误码
        """
        error = self._getDict(f"Error_{error_code}")
        if error:
            error['error_code'] = int(error['error_code'])
            return error
        return None
