"""聊天页面相关的响应函数"""
from datetime import datetime

from flask import Flask, render_template, session, flash, redirect, url_for, request, abort

from service.database.DAO import Database
from service.File import FileManager
from service.response._Utils import _loginCheck


def chatResponse(app: Flask, file_manager: FileManager, db: Database):
    """
    聊天页面相关的响应函数
    :param app: Flask对象，用于添加路由
    :param file_manager: FileManager类对象，用于获取文件路径
    :param db: Database类对象，用于数据库操作
    """

    @app.route('/chat/<int:sender_id>', methods=['GET', 'POST'])
    def chat(sender_id: int):
        """聊天页面"""
        _loginCheck()
        user_id = session.get("login_user").get("id")
        if user_id == sender_id:
            flash("不能和自己聊天哦", "warning")
            return redirect(url_for("home"))
        sender = db.getUser(id=sender_id)
        if not sender:
            abort(404)
        if request.method == "GET":
            sender['profile_photo'] = file_manager.getProfilePhotoPath(sender_id)
            sender['last_time'] = db.getChatLastTime(sender_id, user_id, True)
            chats = db.getChat(sender_id=sender_id, receiver_id=user_id, each=True)
            db.markChatsAsRead(user_id, sender_id)  # user查看了与sender的聊天，则应当将其标记全部标记为已读
            return render_template(
                "chat.html",
                login_user=session.get("login_user"),
                sender=sender,
                chats=chats
            )
        else:
            form = dict(request.form)
            content = form.get('content')
            user_id = session.get("login_user").get("id")
            send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {
                "status": db.addChat(sender_id=user_id, receiver_id=sender_id, send_time=send_time, content=content),
                "content": content,
                "send_time": send_time,
                "profile_photo": file_manager.getProfilePhotoPath(user_id)
            }
