"""与大模型交流相关的响应函数"""
from flask import Flask, request

from service.Network import API
from service.response._Utils import _loginCheck


def lLMResponse(app: Flask, api: API):
    """
    与大模型交流相关的相关路由
    :param app: Flask app
    :param api: API对象，用于获取大语言模型的结果
    """

    @app.route("/query_llm", methods=["POST"])
    def query_llm() -> dict:
        """
        与大模型交流的接口
        :return: dict，格式为{"status": bool, "content": str}，当status为False时说明生成失败，content为失败原因
        """
        _loginCheck()
        prompt = "你是一个擅长文学创作的人。"
        messages = request.json
        if not messages:
            return {"status": False, "content": "参数错误"}
        result = api.getLLMSuggestion_Qwen(messages, prompt)
        if result:
            return {"status": True, "content": result}
        else:
            return {"status": False, "content": "生成失败"}
