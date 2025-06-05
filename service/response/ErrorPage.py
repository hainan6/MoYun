"""自定义HTTP响应，主要包括自定义错误页面等"""
from flask import Flask, abort, render_template, session

from service.database.DAO import Database
from service.File import FileManager
from service.Utils import Config


def getErrorResources(db: Database, file_manager: FileManager, error_code: int) -> dict:
    """
    获取错误页面所需的资源
    :param db: 数据库对象，用于获取错误信息
    :param file_manager: 文件管理器对象，用于获取图片路径
    :param error_code: 错误码
    """
    content = db.getError(error_code)
    author = db.getUser(id=1)
    profile_photo = file_manager.getProfilePhotoPath(author.get("id"))
    if Config["Path"]["ErrorImageSource"] == "local":
        error_image = file_manager.getErrorImagePath(error_code)
    else:
        error_image = f"https://http.cat/{error_code}"
    return {
        "content": content,
        "author": author,
        "profile_photo": profile_photo,
        "error_code": error_code,
        "error_image": error_image
    }


def errorResponse(app: Flask, file_manager: FileManager, db: Database):
    """
    自定义错误页面
    :param app: Flask app
    :param file_manager: 文件管理器对象，用于获取图片路径
    :param db: 数据库对象，用于获取错误信息
    """

    @app.route("/error_sample/<int:error_code>", methods=["GET"])
    def error_sample(error_code):
        """演示自定义错误页面而创建的路由，可以通过/error_sample/<int:error_code>访问，其中error_code为自定义的错误码"""
        abort(error_code)  # 抛出异常，对应的异常将会触发

    @app.errorhandler(400)
    def badRequest(error):
        """400错误页面"""
        return render_template(
            'error.html',
            login_user=session.get('login_user'),
            **getErrorResources(db, file_manager, error.code)
        ), 400

    @app.errorhandler(403)
    def forbidden(error):
        """403错误页面"""
        return render_template(
            'error.html',
            login_user=session.get('login_user'),
            **getErrorResources(db, file_manager, error.code)
        ), 403

    @app.errorhandler(404)
    def pageNotFound(error):
        """404错误页面"""
        return render_template(
            'error.html',
            login_user=session.get('login_user'),
            **getErrorResources(db, file_manager, error.code)
        ), 404

    @app.errorhandler(418)
    def imATeapot(error):
        """418错误页面"""
        return render_template(
            'error.html',
            login_user=session.get('login_user'),
            **getErrorResources(db, file_manager, error.code)
        ), 418

    @app.errorhandler(500)
    def internalServerError(error):
        """500错误页面"""
        return render_template(
            'error.html',
            login_user=session.get('login_user'),
            **getErrorResources(db, file_manager, error.code)
        ), 500

    @app.errorhandler(503)
    def serviceUnavailable(error):
        """503错误页面"""
        return render_template(
            'error.html',
            login_user=session.get('login_user'),
            **getErrorResources(db, file_manager, error.code)
        ), 503
