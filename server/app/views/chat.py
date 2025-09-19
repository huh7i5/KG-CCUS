import os
import json
from flask import Response, request, Blueprint

from app.utils.chat_glm import stream_predict

mod = Blueprint('chat', __name__, url_prefix='/chat')


@mod.route('/', methods=['GET'])
def chat_get():
    return "Chat Get!"


@mod.route('/', methods=['POST'])
def chat():
    request_data = json.loads(request.data)
    # 支持 query 和 prompt 两种字段名
    prompt = request_data.get('query') or request_data.get('prompt')
    history = request_data.get('history', [])

    return Response(response=stream_predict(prompt, history=history), content_type='application/json', status=200)
