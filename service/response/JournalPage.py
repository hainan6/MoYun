"""书评相关页面的响应"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from datetime import datetime
from service import Img
from service.database.DAO import Database
from service.File import FileManager
from service.response._Utils import _loginCheck


def journalResponse(app: Flask, file_manager: FileManager, db: Database):
    """
    书评页面的相关路由
    :param app: Flask应用
    :param file_manager: 文件管理器
    :param db: 数据库
    """

    @app.route("/journal_menu", methods=["GET"])
    def journal_menu():
        """书评主页"""
        _loginCheck()
        # 获取书评列表
        journals = db.getJournal(limit=0)
        for journal_ in journals:
            journal_["account"] = db.getUser(id=journal_.get("author_id")).get("account")
            journal_["header_path"] = file_manager.getJournalHeaderPath(journal_["id"])
            journal_["author_profile_photo"] = file_manager.getProfilePhotoPath(journal_["author_id"])
        return render_template(
            "journal_menu.html",
            login_user=session.get("login_user"),
            journals=journals
        )

    @app.route("/journal/<int:journal_id>", methods=["GET", "POST"])
    def journal(journal_id: int):
        """书评页"""
        journal_ = db.getJournal(id=journal_id)
        if not journal_:
            abort(404)
        if request.method == "GET":  # 查看书评
            journal_header = file_manager.getJournalHeaderPath(journal_["id"])
            author = db.getUser(id=journal_.get("author_id"))
            author['profile_photo'] = file_manager.getProfilePhotoPath(author.get("id"))
            book = db.getBook(id=journal_["book_id"])
            book_cover = file_manager.getBookCoverPath(book["id"])
            # 获取评论
            comments = db.getJournalComment(journal_id=journal_id)
            for comment in comments:
                comment["account"] = db.getUser(id=comment.get("author_id")).get("account")
                comment["profile_photo"] = file_manager.getProfilePhotoPath(comment["author_id"])
            # 标记为已读
            if session.get("login_user") and journal_['author_id'] == session.get("login_user")['id']:
                db.markJournalCommentsAsRead(journal_id)
            return render_template(
                "journal.html",
                login_user=session.get("login_user"),
                author=author,
                journal=journal_,
                journal_header=journal_header,
                book=book,
                book_cover=book_cover,
                comments=comments
            )
        else:  # POST
            _loginCheck()
            data = dict(request.form)
            if "comment_user_id" in data:  # 评论
                comment = data["comment"]
                author_id = int(data["comment_user_id"])
                publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                db.addJournalComment(journal_id, comment, author_id, publish_time)
                author_profile_photo = file_manager.getProfilePhotoPath(author_id)
                return jsonify({
                    "account": session.get("login_user")["account"],
                    "author_id": author_id,
                    "author_profile_photo": author_profile_photo,
                    "publish_time": publish_time,
                    "comment": comment
                })
            elif "like_user_id" in data:  # 点赞
                author_id = data["like_user_id"]
                like_num = db.getJournal(id=journal_id).get("like_num")
                if db.addJournalLike(journal_id, author_id):
                    return {"like_num": like_num + 1, "is_liked": False}
                else:
                    return {"like_num": like_num, "is_liked": True}

    @app.route("/add_journal", methods=["GET", "POST"])
    def add_journal():
        """发表书评"""
        _loginCheck()
        if request.method == "GET":  # 准备写书评
            books = db.getBook(limit=0)
            return render_template(
                "add_journal.html",
                login_user=session.get("login_user"),
                books=books
            )
        else:  # POST，表单中包含了书评内容
            form = dict(request.form)
            form["publish_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            form["author_id"] = session.get("login_user")["id"]
            journal_header = request.files.get("journal_header")  # 书评封面
            journal_id = db.addJournal(**form)
            if journal_header:  # 处理书评封面
                target_path = file_manager.generateJournalHeaderPath(journal_id, abs_path=True)
                journal_header.save(target_path)
                Img.cropImageByScale(target_path, 5, 2)  # 裁剪为'5：2'图片
            flash("发表成功", "success")
            return redirect(url_for("journal", journal_id=journal_id))  # 返回到新书评页
