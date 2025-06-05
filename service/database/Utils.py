"""数据库工具，主要提供信息解析服务，所有从数据库提取数据的函数都在这里实现"""
from typing import TypedDict

from service.database.Model import *


class BookDict(TypedDict):
    """用以描述Book的数据结构(表单)，方法之前传递Book时需要将其作为返回值"""
    id: int
    isbn: str
    title: str
    origin_title: str
    subtitle: str
    author: str
    page: int
    publish_date: str
    publisher: str
    description: str
    douban_score: float
    douban_id: str
    bangumi_score: float
    bangumi_id: str
    type: str


def extractBook(book: Book) -> BookDict:
    """
    提取书籍信息
    """
    return BookDict(
        id=book.id,
        isbn=book.isbn,
        title=book.title,
        origin_title=book.origin_title if book.origin_title else "",
        subtitle=book.subtitle if book.subtitle else "",
        author=book.author,
        page=book.page if book.page else "",
        publish_date=book.publish_date.strftime("%Y-%m-%d") if book.publish_date else "",
        publisher=book.publisher if book.publisher else "",
        description=book.description if book.description else "",
        douban_score=book.douban_score if book.douban_score else "",
        douban_id=book.douban_id if book.douban_id else "",
        bangumi_score=book.bangumi_score if book.bangumi_score else "",
        bangumi_id=book.bangumi_id if book.bangumi_id else "",
        type=book.type if book.type else ""
    )


class ChatDict(TypedDict):
    """用以描述Chat的数据结构(表单)，方法之前传递Chat时需要将其作为返回值"""
    id: int
    sender_id: int
    receiver_id: int
    content: str
    send_time: str
    is_read: bool


def extractChat(chat: Chat) -> ChatDict:
    """
    提取聊天信息
    """
    return ChatDict(
        id=chat.id,
        sender_id=chat.sender_id,
        receiver_id=chat.receiver_id,
        content=chat.content,
        send_time=chat.send_time.strftime("%Y-%m-%d %H:%M:%S") if chat.send_time else "",
        is_read=chat.is_read
    )


class ErrorDict(TypedDict):
    """用以描述Error的数据结构(表单)，方法之前传递Error时需要将其作为返回值"""
    error_code: int
    title: str
    title_en: str
    content: str
    publish_time: str
    reference_link: str


def extractError(error: Error) -> dict:
    """
    提取错误信息
    """
    return ErrorDict(
        error_code=error.error_code,
        title=error.title,
        title_en=error.title_en,
        content=error.content,
        publish_time=error.publish_time.strftime("%Y-%m-%d %H:%M:%S") if error.publish_time else "",
        reference_link=error.reference_link
    )


class GroupDict(TypedDict):
    """用以描述Group的数据结构(表单)，方法之前传递Group时需要将其作为返回值"""
    id: int
    name: str
    founder_id: int
    establish_time: str
    description: str


def extractGroup(group: Group) -> GroupDict:
    """
    提取小组信息
    """
    return GroupDict(
        id=group.id,
        name=group.name,
        founder_id=group.founder_id,
        establish_time=group.establish_time.strftime("%Y-%m-%d %H:%M:%S") if group.establish_time else "",
        description=group.description
    )


class GroupDiscussionDict(TypedDict):
    """用以描述GroupDiscussion的数据结构(表单)，方法之前传递GroupDiscussion时需要将其作为返回值"""
    id: int
    poster_id: int
    group_id: int
    post_time: str
    title: str
    content: str
    is_read: bool


def extractGroupDiscussion(groupDiscussion: GroupDiscussion) -> GroupDiscussionDict:
    """
    提取小组讨论信息
    """
    return GroupDiscussionDict(
        id=groupDiscussion.id,
        poster_id=groupDiscussion.poster_id,
        group_id=groupDiscussion.group_id,
        post_time=groupDiscussion.post_time.strftime("%Y-%m-%d %H:%M:%S") if groupDiscussion.post_time else "",
        title=groupDiscussion.title,
        content=groupDiscussion.content,
        is_read=groupDiscussion.is_read
    )


class GroupDiscussionReplyDict(TypedDict):
    """用以描述GroupDiscussionReply的数据结构(表单)，方法之前传递GroupDiscussionReply时需要将其作为返回值"""
    author_id: int
    discussion_id: int
    reply_time: str
    content: str
    is_read: bool


def extractGroupDiscussionReply(groupDiscussionReply: GroupDiscussionReply) -> GroupDiscussionReplyDict:
    """
    提取小组讨论回复信息
    """
    return GroupDiscussionReplyDict(
        author_id=groupDiscussionReply.author_id,
        discussion_id=groupDiscussionReply.discussion_id,
        reply_time=groupDiscussionReply.reply_time.strftime(
            "%Y-%m-%d %H:%M:%S") if groupDiscussionReply.reply_time else "",
        content=groupDiscussionReply.content,
        is_read=groupDiscussionReply.is_read
    )


class GroupUserDict(TypedDict):
    """用以描述GroupUser的数据结构(表单)，方法之前传递GroupUser时需要将其作为返回值"""
    user_id: int
    group_id: int
    join_time: str


def extractGroupUser(groupUser: GroupUser) -> GroupUserDict:
    """
    提取小组用户信息
    """
    return GroupUserDict(
        user_id=groupUser.user_id,
        group_id=groupUser.group_id,
        join_time=groupUser.join_time
    )


class JournalDict(TypedDict):
    """用以描述Journal的数据结构(表单)，方法之前传递Journal时需要将其作为返回值"""
    id: int
    title: str
    first_paragraph: str
    content: list[str]
    publish_time: str
    author_id: int
    book_id: int
    like_num: Union[int, None]
    comment_num: Union[int, None]


def extractJournal(journal: Journal, comment_num: int = 0, like_num: int = 0) -> JournalDict:
    """
    提取书评信息
    :param journal: 书评对象
    :param like_num: 点赞数
    :param comment_num: 评论数
    """
    return JournalDict(
        id=journal.id,
        title=journal.title,
        first_paragraph=journal.first_paragraph,
        content=journal.content.split("\n"),
        publish_time=journal.publish_time.strftime("%Y-%m-%d %H:%M:%S") if journal.publish_time else "",
        author_id=journal.author_id,
        book_id=journal.book_id,
        like_num=like_num,
        comment_num=comment_num
    )


class JournalCommentDict(TypedDict):
    """用以描述JournalComment的数据结构(表单)，方法之前传递JournalComment时需要将其作为返回值"""
    id: int
    publish_time: str
    author_id: int
    journal_id: int
    content: str
    is_read: bool


def extractJournalComment(comment: JournalComment) -> JournalCommentDict:
    """
    提取书评的评论信息
    :param comment: 书评评论对象
    """
    return JournalCommentDict(
        id=comment.id,
        publish_time=comment.publish_time.strftime("%Y-%m-%d %H:%M:%S") if comment.publish_time else "",
        author_id=comment.author_id,
        journal_id=comment.journal_id,
        content=comment.content,
        is_read=comment.is_read
    )


class JournalLikeDict(TypedDict):
    """用以描述JournalLike的数据结构(表单)，方法之前传递JournalLike时需要将其作为返回值"""
    author_id: int
    journal_id: int
    publish_time: str


def extractJournalLike(like: JournalLike):
    """
    提取书评的点赞信息
    :param like: 书评点赞对象
    """
    return JournalLikeDict(
        author_id=like.author_id,
        journal_id=like.journal_id,
        publish_time=like.publish_time.strftime("%Y-%m-%d %H:%M:%S") if like.publish_time else ""
    )


class UserDict(TypedDict):
    """用以描述User的数据结构(表单)，方法之前传递User时需要将其作为返回值"""
    id: int
    account: str
    password: Union[str, None]
    signature: str
    email: str
    telephone: str
    role: str


def extractUser(user: User, with_password: bool = False) -> UserDict:
    """
    提取用户信息
    :param user: 用户对象
    :param with_password: 返回值是否是否密码
    """
    if with_password:
        return UserDict(
            id=user.id,
            account=user.account,
            password=user.password,
            signature=user.signature,
            email=user.email,
            telephone=user.telephone,
            role=user.role
        )
    else:
        return UserDict(
            id=user.id,
            account=user.account,
            password=None,
            signature=user.signature,
            email=user.email,
            telephone=user.telephone,
            role=user.role
        )


class UnreadMessagesDict(TypedDict):
    """用以描述未读消息的数据结构(表单)"""
    journal_comments: list[JournalCommentDict]
    group_discussions: list[GroupDiscussionDict]
    discussion_replies: list[GroupDiscussionReplyDict]
    chats: list[ChatDict]
