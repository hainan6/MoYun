"""圈子页面相关的响应函数"""
from datetime import datetime

from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify, abort

from service import Img
from service.database.DAO import Database
from service.File import FileManager
from service.response._Utils import _loginCheck


def groupResponse(app: Flask, file_manager: FileManager, db: Database) -> None:
    """
    圈子页面的相关路由
    :param app: Flask app
    :param file_manager: 文件管理器对象，用于获取图片路径
    :param db: 数据库对象，用于获取圈子信息
    """

    @app.route("/group", methods=["GET"])
    def self_group():
        """如果只是访问/group，重定向到圈子主页"""
        return redirect(url_for("group_menu"))

    @app.route("/group_menu", methods=["GET"])
    def group_menu():
        """圈子主页"""
        _loginCheck()
        groups = db.getGroup(limit=0)
        for group_ in groups:
            group_["group_icon"] = file_manager.getGroupIconPath(group_["id"])
            group_["user_num"] = db.getGroupUsersNum(group_["id"])
            group_["discussion_num"] = db.getGroupDiscussionNum(group_id=group_["id"])
        return render_template(
            "group_menu.html",
            login_user=session.get("login_user"),
            groups=groups
        )

    @app.route("/group/<int:group_id>", methods=["GET"])
    def group(group_id: int):
        """圈子页面"""
        _loginCheck()
        group_ = db.getGroup(id=group_id)
        if not group_:
            abort(404)
        group_['account'] = db.getUser(id=group_.get("founder_id")).get("account")
        if session.get("login_user")["id"] == group_["founder_id"]:
            db.markGroupDiscussionsAsRead(group_id)
        discussions_info = db.getGroupDiscussion(limit=0, group_id=group_id)
        for discussion_ in discussions_info:
            discussion_["account"] = db.getUser(id=discussion_.get("poster_id")).get("account")
            discussion_["reply_num"] = db.getGroupDiscussionReplyNum(discussion_id=discussion_["id"])
        group_["group_icon"] = file_manager.getGroupIconPath(group_id)
        group_users = db.getGroupUser(limit=0, group_id=group_id)  # groupUser列表
        for user in group_users:
            user["account"] = db.getUser(id=user.get("user_id")).get("account")
            user['profile_photo'] = file_manager.getProfilePhotoPath(user['user_id'])
        replies = db.getGroupReply(group_id)
        for reply in replies:
            reply["account"] = db.getUser(id=reply.get("author_id")).get("account")
            reply["profile_photo"] = file_manager.getProfilePhotoPath(reply["author_id"])
        return render_template(
            "group.html",
            login_user=session.get("login_user"),
            group=group_,
            group_users=group_users,
            discussions=discussions_info,
            replies=replies,
        )

    @app.route("/edit_group/<int:group_id>", methods=["GET", "POST"])
    def edit_group(group_id: int):
        """编辑圈子信息页面"""
        _loginCheck()
        group_ = db.getGroup(id=group_id)  # group信息
        if not group_:
            abort(404)
        group_['account'] = db.getUser(id=group_.get("founder_id")).get("account")
        group_["group_icon"] = file_manager.getGroupIconPath(group_id)

        if session.get("login_user").get("id") != group_['founder_id']:
            flash("您没有权限", "info")
            return redirect(url_for("home"))
        if request.method == "GET":
            discussions = db.getGroupDiscussion(limit=0, group_id=group_id)  # discussion信息
            for discussion_ in discussions:
                discussion_["account"] = db.getUser(id=discussion_.get("poster_id")).get("account")
                discussion_["reply_num"] = db.getGroupDiscussionReplyNum(discussion_id=discussion_["id"])
            group_users = db.getGroupUser(limit=0, group_id=group_id)  # groupUser列表
            for user in group_users:
                user["account"] = db.getUser(id=user.get("user_id")).get("account")
                user['profile_photo'] = file_manager.getProfilePhotoPath(user['user_id'])
            return render_template(
                "edit_group.html",
                login_user=session.get("login_user"),
                discussions=discussions,
                group=group_,
                group_users=group_users
            )
        else:  # POST
            form = dict(request.form)
            if form['operation'] == 'delete_discussion':
                if db.deleteGroupDiscussion(int(form['discussion_id'])):
                    flash("删除成功", "success")
                    return jsonify({'status': 'success'})
                else:
                    flash("删除失败", "error")
                    return jsonify({'status': 'error'})
            elif form['operation'] == 'delete_user':
                if db.deleteGroupUser(group_id, int(form['user_id'])):
                    flash("删除成功", "success")
                    return jsonify({'status': 'success'})
                else:
                    flash("删除失败", "error")
                    return jsonify({'status': 'error'})
            elif form['operation'] == 'edit_group_info':
                name, description = form['group_name'], form['group_description']
                icon = request.files.get("group_icon")
                res = db.modifyGroup(group_id, name=name, description=description)
                flash("更新成功", "success") if res else flash("更新失败", "error")
                if icon:
                    targetPath = file_manager.generateGroupIconPath(group_id, abs_path=True)
                    file_manager.deleteGroupIcon(group_id)
                    icon.save(targetPath)
                    Img.cropImageSquare(targetPath)
                return redirect(url_for("group", group_id=group_id))

    @app.route("/add_group", methods=["GET", "POST"])
    def add_group():
        """创建圈子页面"""
        _loginCheck()
        if request.method == "GET":
            return render_template(
                "add_group.html",
                login_user=session.get("login_user")
            )
        else:
            group_icon = request.files.get("group_icon")
            name = request.form.get("name")
            description = request.form.get("description")
            founder_id = session.get("login_user")["id"]
            establish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            group_id = db.addGroup(name, description, founder_id, establish_time)
            if group_icon:
                target_path = file_manager.generateGroupIconPath(group_id, abs_path=True)
                group_icon.save(target_path)
                Img.cropImageSquare(target_path)  # 裁剪为正方形
                flash("创建成功", "success")
            return redirect(url_for("group", group_id=group_id))

    @app.route("/discussion/<int:discussion_id>", methods=["GET", "POST"])
    def discussion(discussion_id: int):
        """帖子页面"""
        _loginCheck()
        discussion_ = db.getGroupDiscussion(id=discussion_id)
        if not discussion_:
            abort(404)
        if request.method == "GET":  # 查看帖子
            author = db.getUser(id=discussion_.get("poster_id"))
            author['profile_photo'] = file_manager.getProfilePhotoPath(author.get('id'))
            discussion_reply = db.getGroupDiscussionReplies(limit=0, discussion_id=discussion_id)
            if session.get("login_user")["id"] == discussion_["poster_id"]:
                db.markDiscussionRepliesAsRead(discussion_id)
            for reply in discussion_reply:
                reply["account"] = db.getUser(id=reply.get("author_id")).get("account")
                reply["profile_photo"] = file_manager.getProfilePhotoPath(reply.get("author_id"))
            return render_template(
                "discussion.html",
                login_user=session.get("login_user"),
                discussion=discussion_,
                author=author,
                discussion_reply=discussion_reply
            )
        elif request.method == "POST":  # 发表回帖
            reply_content = request.form.get('reply_content')
            reply_user_id = session.get('login_user').get('id')
            reply_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.addGroupDiscussionReply(reply_user_id, discussion_id, reply_content, reply_time)
            author_profile_photo = file_manager.getProfilePhotoPath(reply_user_id)
            return jsonify({
                'account': session.get("login_user")['account'],
                'author_id': reply_user_id,
                'author_profile_photo': author_profile_photo,
                'reply_time': reply_time,
                'reply_content': reply_content
            })

    @app.route("/add_discussion/<int:group_id>", methods=["GET", "POST"])
    def add_discussion(group_id: int):
        """发表帖子页面"""
        _loginCheck()
        group_ = db.getGroup(id=group_id)
        if not group_:
            abort(404)
        if request.method == "GET":
            return render_template(
                "add_discussion.html",
                login_user=session.get("login_user"),
                group=group_
            )
        else:  # 发表帖子
            form = dict(request.form)
            if not form.get("title") or not form.get("content"):
                flash("标题和内容不能为空", "error")
                return redirect(url_for("add_discussion", group_id=group_id))
            poster_id = session.get("login_user")["id"]
            post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            id_ = db.addGroupDiscussion(poster_id=poster_id, group_id=group_id, post_time=post_time, **form)
            flash("发表成功", "success")
            return redirect(url_for("discussion", discussion_id=id_))
