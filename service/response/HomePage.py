"""首页相关的响应函数"""
from flask import Flask, render_template, session, request

from service.database.DAO import Database
from service.File import FileManager
from service.Network import API
from service.response._Utils import _loginCheck


def homepageResponse(app: Flask, file_manager: FileManager, db: Database, api: API):
    """
    首页的相关路由
    :param app: Flask app
    :param file_manager: 文件管理器对象，用于获取图片路径
    :param db: 数据库对象，用于获取数据
    :param api: API对象，用于获取天气和诗词信息
    """

    @app.route("/home", methods=["GET"])
    def home():
        """首页"""
        _loginCheck()
        # 获取天气信息
        weather = api.getWeather_YiKeTianQi(request.remote_addr)
        # 获取首页相关信息
        journals = db.getJournal(limit=5)
        unread_message_num = db.getAllUnreadMessageNum(session.get("login_user")['id'])
        for journal in journals:
            journal["header_path"] = file_manager.getJournalHeaderPath(journal["id"])
            journal['author_profile_photo'] = file_manager.getProfilePhotoPath(journal['author_id'])
        return render_template(
            "home.html",
            login_user=session.get("login_user"),
            journals=journals,
            weather=weather,
            unread_message_num=unread_message_num
        )
