"""书籍页面相关的响应函数"""
from flask import Flask, render_template, request, session, flash, redirect, url_for, abort

from service.database.DAO import Database
from service.File import FileManager
from service.response._Utils import _loginCheck


def bookResponse(app: Flask, file_manager: FileManager, db: Database):
    """
    书籍页面的相关路由
    :param app: Flask app
    :param file_manager: 文件管理器对象，用于获取图片路径
    :param db: 数据库对象，用于获取书籍信息
    """

    @app.route("/book_menu", methods=["GET"])
    def book_menu():
        """书籍首页"""
        _loginCheck()
        books = db.getBook(limit=0)
        for book_ in books:
            book_["book_cover"] = file_manager.getBookCoverPath(book_["id"])
        return render_template(
            "book_menu.html",
            login_user=session.get("login_user"),
            books=books
        )

    @app.route("/book/<int:book_id>", methods=["GET"])
    def book(book_id: int):
        """书籍详情页"""
        _loginCheck()
        book_ = db.getBook(id=book_id)
        if not book_:
            abort(404)
        book_cover = file_manager.getBookCoverPath(book_id)
        return render_template(
            "book.html",
            login_user=session.get("login_user"),
            book=book_,
            book_cover=book_cover
        )

    @app.route("/add_book", methods=["GET", "POST"])
    def add_book():
        """添加书籍"""
        _loginCheck()
        if session.get("login_user").get("role") != "admin" and session.get("login_user").get("role") != "teacher":
            flash("您没有权限", "info")
            return abort(403)
        if request.method == "GET":
            return render_template(
                "add_book.html",
                login_user=session.get("login_user")
            )
        else:
            form = dict(request.form)
            book_cover = request.files.get("book_cover")
            book_id = db.addBook(**form)
            if book_cover:
                target_path = file_manager.generateBookCoverPath(book_id, abs_path=True)
                book_cover.save(target_path)
                flash("添加成功", "error")
                return redirect(url_for("book", book_id=book_id))
            else:
                flash("添加失败，请检查是否已有该书，或是否未填写完必要信息", "error")
                return redirect(url_for("book_menu"))

    @app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
    def edit_book(book_id: int):
        """修改书籍"""
        _loginCheck()
        if session.get("login_user").get("role") != "admin" and session.get("login_user").get("role") != "teacher":
            flash("您没有权限", "info")
            return abort(403)
        book_ = db.getBook(id=book_id)
        if not book_:
            abort(404)
        # 加载修改书籍的界面
        if request.method == "GET":
            book_cover = file_manager.getBookCoverPath(book_id)
            return render_template(
                "edit_book.html",
                login_user=session.get("login_user"),
                book=book_,
                book_cover=book_cover
            )
        elif request.method == "POST":
            form = dict(request.form)
            if db.modifyBook(book_id, **form):
                flash("修改成功", "success")
            else:
                flash("修改失败", "error")
            return redirect(url_for("book", book_id=book_id))
