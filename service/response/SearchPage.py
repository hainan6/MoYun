"""搜索页的相关路由"""
from datetime import datetime

from flask import abort, Flask, render_template, request, session

from service.File import FileManager
from service.database.DAO import Database
from service.response._Utils import _loginCheck


def searchResponse(app: Flask, file_manager: FileManager, db: Database):
    """
    搜索页面的相关路由
    :param app: Flask应用
    :param file_manager: 文件管理器
    :param db: 数据库
    """

    @app.route("/search", methods=["GET"])
    def search():
        """搜索页面"""
        _loginCheck()
        search_start_time = datetime.now()
        search_type = request.args.get("type")
        keyword = request.args.get("keyword")

        if search_type == "journal":
            results = db.getJournal(limit=0, keyword=keyword)
            for i in range(len(results)):
                results[i]["header"] = file_manager.getJournalHeaderPath(results[i].get("id"))
                results[i]["search_type"] = "journal"
        elif search_type == "book":
            results = db.getBook(limit=0, keyword=keyword)
            for i in range(len(results)):
                results[i]["book_cover"] = file_manager.getBookCoverPath(results[i].get("id"))
                results[i]["search_type"] = "book"
        elif search_type == "group":
            results = db.getGroup(limit=0, keyword=keyword)
            for i in range(len(results)):
                results[i]["group_icon"] = file_manager.getGroupIconPath(results[i].get("id"))
                results[i]["founder"] = db.getUser(id=results[i]["founderID"]).get("account")
                results[i]["search_type"] = "group"
        elif search_type == "user":
            results = db.getUser(limit=0, keyword=keyword)
            for i in range(len(results)):
                results[i]["profile_photo"] = file_manager.getProfilePhotoPath(results[i].get("id"))
                results[i]["search_type"] = "user"
        elif search_type == "all":
            users = db.getUser(limit=0, keyword=keyword)
            for i in range(len(users)):
                users[i]["profile_photo"] = file_manager.getProfilePhotoPath(users[i].get("id"))
                users[i]["search_type"] = "user"
            groups = db.getGroup(limit=0, keyword=keyword)
            for i in range(len(groups)):
                groups[i]["group_icon"] = file_manager.getGroupIconPath(groups[i].get("id"))
                groups[i]["founder"] = db.getUser(id=groups[i]["founderID"]).get("account")
                groups[i]["search_type"] = "group"
            books = db.getBook(limit=0, keyword=keyword)
            for i in range(len(books)):
                books[i]["book_cover"] = file_manager.getBookCoverPath(books[i].get("id"))
                books[i]["search_type"] = "book"
            journals = db.getJournal(limit=0, keyword=keyword)
            for i in range(len(journals)):
                journals[i]["header"] = file_manager.getJournalHeaderPath(journals[i].get("id"))
                journals[i]["search_type"] = "journal"
            results = users + groups + books + journals
        else:
            abort(400)  # 参数错误，返回400错误
        cost_time = (datetime.now() - search_start_time).total_seconds()
        return render_template(
            "search.html",
            login_user=session.get("login_user"),
            keyword=keyword,
            results=results,
            cost_time=cost_time,
            search_type=search_type
        )
