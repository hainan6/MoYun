"""使用Torando启动Flask应用"""
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from app import app

s = HTTPServer(WSGIContainer(app))
s.listen(5000)  # 监听 5000 端口
IOLoop.current().start()
