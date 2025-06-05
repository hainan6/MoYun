"""消息中心相关的路由响应函数"""
from flask import Flask, session, render_template, request

from service.database.DAO import Database
from service.database.Utils import UnreadMessagesDict
from service.File import FileManager
from service.response._Utils import _loginCheck


def messageResponse(app: Flask, file_manager: FileManager, db: Database):
    """
    消息中心的相关路由
    :param app: Flask应用
    :param file_manager: 文件管理器
    :param db: 数据库
    """

    @app.route("/message", methods=["GET", "POST"])
    def message():
        """消息中心页"""
        _loginCheck()
        if request.method == "GET":
            # 获取全部的未读信息
            messages: UnreadMessagesDict = db.getAllUnreadMessage(user_id=session.get("login_user").get("id"))
            journal_comments = messages.get('journal_comments')
            group_discussions = messages.get('group_discussions')
            discussion_replies = messages.get('discussion_replies')
            chats = messages.get('chats')

            # 根据未读的journal_comments获取对应的journal
            journal_ids = []
            for comment in journal_comments:
                journal_id = comment.get('journal_id')
                if journal_id not in journal_ids:  # 去重
                    journal_ids.append(journal_id)
            journals = [db.getJournal(id=journal_id) for journal_id in journal_ids]
            for journal in journals:
                journal['header_path'] = file_manager.getJournalHeaderPath(journal.get('id'))
                journal['author_profile_photo'] = file_manager.getProfilePhotoPath(journal.get('author_id'))

            # 根据未读的group_discussions获取对应的group
            group_ids = []
            for discussion in group_discussions:
                group_id = discussion.get('group_id')
                if group_id not in group_ids:  # 去重
                    group_ids.append(group_id)
            groups = [db.getGroup(id=group_id) for group_id in group_ids]
            for group in groups:
                group['icon'] = file_manager.getGroupIconPath(group.get('id'))
                group['founder_account'] = db.getUser(id=group.get('founder_id')).get('account')
                group['discussion_num'] = db.getGroupDiscussionNum(group_id=group.get('id'))

            # 根据未读的discussion_replies获取对应的discussion
            discussion_ids = []
            for reply in discussion_replies:
                discussion_id = reply.get('discussion_id')
                if discussion_id not in discussion_ids:
                    discussion_ids.append(discussion_id)
            discussions = [db.getGroupDiscussion(id=discussion_id) for discussion_id in discussion_ids]
            for discussion in discussions:
                discussion['author_profile_photo'] = file_manager.getProfilePhotoPath(discussion.get('author_id'))
                discussion['author_account'] = db.getUser(id=discussion.get('poster_id')).get('account')
                discussion['reply_num'] = db.getGroupDiscussionReplyNum(discussion_id=discussion.get('id'))

            # 根据未读的chats获取对应的sender
            sender_ids = []
            for chat in chats:
                sender_id = chat.get('sender_id')
                if sender_id not in sender_ids:
                    sender_ids.append(sender_id)
            senders = [db.getUser(id=sender_id) for sender_id in sender_ids]
            for sender in senders:
                sender['chat_num'] = db.getChatNum(
                    sender_id=sender.get('id'),
                    receiver_id=session.get("login_user").get("id"),
                    each=True
                )
                sender['last_chat_time'] = db.getChatLastTime(
                    sender_id=sender.get('id'),
                    receiver_id=session.get("login_user").get("id")
                )
                sender['profile_photo'] = file_manager.getProfilePhotoPath(sender.get('id'))

            return render_template(
                "message.html",
                login_user=session.get("login_user"),
                journals=journals,
                journal_comments=journal_comments,
                groups=groups,
                group_discussions=group_discussions,
                discussions=discussions,
                discussion_replies=discussion_replies,
                chats=chats,
                senders=senders
            )
        else:  # POST，是标记已读行为，根据表单里的type和id来执行对应的操作
            form = dict(request.form)
            user_id = session.get("login_user").get("id")
            id_ = form.get('id')
            if form.get('type') == 'journal' and user_id == db.getJournal(id=id_).get('author_id'):
                status = db.markJournalCommentsAsRead(id_)
            elif form.get('type') == 'group' and user_id == db.getGroup(id=id_).get('founder_id'):
                status = db.markGroupDiscussionsAsRead(id_)
            elif form.get('type') == 'discussion' and user_id == db.getGroupDiscussion(id=id_).get('poster_id'):
                status = db.markDiscussionRepliesAsRead(id_)
            elif form.get('type') == 'sender':
                status = db.markChatsAsRead(session.get("login_user").get("id"), id_)
            else:
                status = False
            return {"status": status}
