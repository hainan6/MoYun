"""登录前的欢迎页"""
from flask import request, render_template, redirect, url_for, session, flash, Flask
import random
from service.database.DAO import Database
from service.File import FileManager
from service.Network import Mail


def accountResponse(app: Flask, file_manager: FileManager, db: Database, mail: Mail):
    """
    账号行为页面的相关路由
    :param app: Flask应用
    :param file_manager: 文件管理器
    :param db: 数据库
    :param mail: 邮件服务
    """

    @app.route("/", methods=["GET", "POST"])  # 1.欢迎页
    def index():
        """初始页"""
        if request.method == "POST":  # 用户发起登录请求
            # 获取表单数据
            account = request.form.get("account")
            password = request.form.get("password")
            # 验证用户名和密码是否正确
            user_id = db.checkLogin(account, password)
            if user_id:  # 如果验证成功，跳转到首页
                session["login_user"] = db.getUser(id=user_id)  # 记录登录用户信息
                session["login_user"]["profile_photo"] = file_manager.getProfilePhotoPath(session["login_user"]["id"])
                db.modifyUser(filter_id=session["login_user"]["id"])  # 更新登录时间
                flash("登录成功", "success")
                return redirect(url_for("home"))
            else:  # 如果验证失败，跳转回登录页面
                flash("用户名或密码错误", "error")
                return redirect(url_for("index"))
        else:  # 用户发起访问请求
            if session.get("login_user"):  # 如果用户已经登录，跳转到首页
                return redirect(url_for("home"))
            return render_template("index.html")  # 否则返回欢迎页

    @app.route("/register", methods=["POST"])
    def register():
        """注册页"""
        if request.method == "POST":  # POST，则需要获取表单数据
            account = request.form.get("account")
            password = request.form.get("password")
            email = request.form.get("email")
            telephone = request.form.get("telephone")
            if not account or not password or not email:
                flash("账号、密码、邮箱是必须的", "warning")
                return redirect(url_for("index") + "#register")
            # 验证用户名和密码是否可用
            if db.getUser(account=account):
                flash("用户名已存在，请尝试登录或找回密码", "info")
                return redirect(url_for("index") + "#login")
            else:
                db.addUser(account=account, raw_password=password, email=email, telephone=telephone)
                flash("注册成功，请登录", "success")
                return redirect(url_for("index") + "#login")

    @app.route("/sendCaptcha", methods=["POST"])
    def sendCaptcha():
        """发送验证码"""
        if request.method == "POST":
            account = request.form.get("account")
            user = db.getUser(account=account)
            if not user:
                flash("用户名不存在，请先注册", "info")
                return redirect(url_for("index") + "#register")
            email = user["email"]
            captcha = str(random.randint(100000, 999999))
            mail.sendCaptcha(email, captcha)
            session["captcha"] = captcha
            session["resetPasswdAccount"] = account
            flash("验证码已发送，请注意查收", "success")
            return redirect(url_for("index") + "#resetPasswd")

    @app.route("/resetPasswd", methods=["POST", "GET"])
    def resetPasswd():
        """重置密码"""
        if request.method == "POST":
            account = session.get("resetPasswdAccount")
            captcha = request.form.get("captcha")
            password = request.form.get("password")
            if captcha != session.get("captcha"):
                flash("验证码错误", "warning")
                return redirect(url_for("index") + "#resetPasswd")
            else:
                db.modifyUser(filter_account=account, password=password)
                flash("密码修改成功，请重新登录", "success")
                return redirect(url_for("index") + "#login")

    @app.route("/logout", methods=["GET"])
    def logout():
        """登出"""
        if session.get("login_user"):
            session.pop("login_user")
            response = redirect(url_for("index"))
            response.delete_cookie('session')
            flash("您已成功退出账号", "success")
            return response
        else:
            return redirect(url_for("index"))
