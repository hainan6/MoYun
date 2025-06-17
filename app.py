"""
Legacy Application Entry Point
Preserved for backward compatibility - Consider using application.py for new deployments

This file maintains the original structure for compatibility with existing deployments.
For new features and better architecture, please use the refactored application.py
"""
import os

from flask import Flask

from service import Utils
from service.database.DAO import Database
from service.File import FileManager
from service.Network import API, Mail
from service.response import *

# Add deprecation warning
import warnings
warnings.warn(
    "app.py is deprecated. Please consider migrating to application.py for better architecture and features.",
    DeprecationWarning,
    stacklevel=2
)

# 创建全局变量：应用、服务
app = Flask(
    __name__,
    template_folder=(os.getcwd() + "/templates").replace("\\", "/"),
    static_folder=(os.getcwd() + "/static").replace("\\", "/")
)  # app作为全局变量，并指定部分资源的路径
app.config.update(Utils.queryConfig('Flask'))  # 从配置文件中读取Flask配置

# 配置服务
api = API()
mail = Mail()
db = Database(app)
file_manager = FileManager()

accountResponse(app, file_manager, db, mail)  # 账号行为页面的相关路由
bookResponse(app, file_manager, db)  # 书籍页面的相关路由
chatResponse(app, file_manager, db)  # 聊天页面的相关路由
homepageResponse(app, file_manager, db, api)  # 首页的相关路由
errorResponse(app, file_manager, db)  # 附加自定义的错误页面
journalResponse(app, file_manager, db)  # 书评页面的相关路由
lLMResponse(app, api)  # 与大模型交流相关的相关路由
profileResponse(app, file_manager, db)  # 个人信息页面的相关路由
groupResponse(app, file_manager, db)  # 圈子页面的相关路由
searchResponse(app, file_manager, db)  # 搜索页面的相关路由
messageResponse(app, file_manager, db)  # 消息中心的相关路由
securityCheck(app)  # 安全检查相关措施

if __name__ == "__main__":
    app.run(
        port=Utils.queryConfig("Flask", "Port"),
        debug=True,
        host="0.0.0.0"
    )
