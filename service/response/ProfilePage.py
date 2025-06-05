"""个人信息页面的相关路由"""
from flask import render_template, session, redirect, url_for, flash, request, abort, Flask
from service import Img
from service.File import FileManager
from service.database.DAO import Database
from service.response._Utils import _loginCheck


def profileResponse(app: Flask, file_manager: FileManager, db: Database):
    """
    个人信息页面的相关路由
    :param app: Flask应用
    :param file_manager: 文件管理器
    :param db: 数据库
    """

    @app.route("/profile", endpoint="self_profile", methods=["GET"])
    def self_profile():
        """访问/profile，重定向到自己的个人信息页"""
        _loginCheck()
        return redirect(url_for("profile", user_id=session.get("login_user")['id']))

    @app.route("/profile/", methods=["GET"])
    def default_profile():
        """访问/profile/，重定向到自己的个人信息页"""
        return redirect(url_for("self_profile"))

    @app.route("/profile/<int:user_id>", endpoint="profile", methods=["GET"])
    def profile(user_id: int):  # 个人信息页(注意，不一定是自己)
        """个人信息页"""
        _loginCheck()
        user = db.getUser(id=user_id)
        if not user:
            abort(404)
        journals = db.getJournal(limit=0, author_id=user_id)
        profile_photo = file_manager.getProfilePhotoPath(user_id)
        return render_template(
            "profile.html",
            login_user=session.get("login_user"),
            user=user,
            journals=journals,
            profile_photo=profile_photo
        )

    @app.route("/edit_profile", methods=["GET", "POST"])
    def edit_profile():
        """编辑个人信息"""
        _loginCheck()
        if request.method == "POST":
            user_id = session.get("login_user")['id']
            account = request.form.get("account")
            signature = request.form.get("signature")
            email = request.form.get("email")
            telephone = request.form.get("telephone")
            db.modifyUser(filter_id=user_id, account=account, signature=signature, email=email, telephone=telephone)
            profile_photo = request.files.get("profile_photo")
            if profile_photo:
                photo_path = file_manager.getProfilePhotoPath(user_id, abs_path=True, enable_default=False)
                if not photo_path:  # 之前没设置过头像，使用的应该是默认头像
                    photo_path = file_manager.generateProfilePhotoPath(user_id, abs_path=True)
                file_manager.deleteProfilePhoto(user_id)  # 删除原有头像
                profile_photo.save(photo_path)  # 保存新头像
                Img.cropImageSquare(photo_path)  # 裁剪成正方形
            flash("修改成功", "success")
            session["login_user"] = db.getUser(id=user_id)  # 更新session中的用户信息
            session["login_user"]["profile_photo"] = file_manager.getProfilePhotoPath(user_id)
            return redirect(f"/profile/{user_id}")
        else:
            profile_photo = file_manager.getProfilePhotoPath(session.get("login_user")["id"])
            return render_template(
                "edit_profile.html",
                login_user=session.get("login_user"),
                profile_photo=profile_photo
            )
