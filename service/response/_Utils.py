"""response模块的工具函数"""
from typing import Literal

from flask import abort, session, flash, url_for, Flask, request
from flask import redirect as flask_redirect
import re


def _loginCheck(redirect: Literal["index", 401, 403] = "index"):
    """
    检查用户是否登录，未登录则
    :param redirect: 重定向的页面，默认为"index"，即未登录前的欢迎页，401或403则直接返回401(Unauthorized)或403(Forbidden)错误
    :return: None
    """
    if not session.get('login_user'):
        flash('请先登录', 'warning')

        if redirect == "index":
            return flask_redirect(url_for('index'))
        elif redirect == 401:
            abort(401)
        elif redirect == 403:
            abort(403)
        else:
            raise ValueError("Invalid 'redirect' value")


def securityCheck(app: Flask):
    """
    进行安全方面的检查
    """

    @app.before_request
    def checkUA():
        """
        检查用户代理是否为浏览器
        """
        browser_identifiers = ["Mozilla", "Firefox", "Chrome", "Safari", "Opera", "MSIE", "Trident", "Edge"]
        if (
                'User-Agent' not in request.headers
                or not request.headers['User-Agent']
                or re.search(r"(" + "|".join(browser_identifiers) + r")", request.headers['User-Agent']) is None
        ):
            abort(418)
