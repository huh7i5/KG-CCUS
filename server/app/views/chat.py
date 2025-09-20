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
    print("🌐 [BACKEND] ================== 新的聊天请求 ==================")

    try:
        # 解析请求数据
        print("📥 [BACKEND] 解析请求数据...")
        request_data = json.loads(request.data)
        print(f"📥 [BACKEND] 请求数据大小: {len(request.data)} bytes")
        print(f"📥 [BACKEND] 请求数据结构: {list(request_data.keys())}")

        # 支持 query 和 prompt 两种字段名
        prompt = request_data.get('query') or request_data.get('prompt')
        history = request_data.get('history', [])

        print(f"💬 [BACKEND] 用户输入: {prompt}")
        print(f"📚 [BACKEND] 历史记录长度: {len(history)}")

        if not prompt:
            print("❌ [BACKEND] 错误：没有提供prompt")
            error_response = json.dumps({
                "error": "No prompt provided",
                "updates": {"response": "错误：没有提供问题内容"}
            }, ensure_ascii=False)
            return Response(response=error_response, content_type='application/json', status=400)

        print("🔄 [BACKEND] 开始调用stream_predict函数...")

        # 包装stream_predict以添加调试信息
        def debug_stream_predict():
            chunk_count = 0
            for chunk in stream_predict(prompt, history=history):
                chunk_count += 1
                print(f"📤 [BACKEND] 发送第{chunk_count}个数据块，大小: {len(chunk)} bytes")

                try:
                    # 尝试解析JSON以验证格式
                    decoded_chunk = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                    parsed_data = json.loads(decoded_chunk.strip())
                    print(f"📤 [BACKEND] 数据块内容结构: {list(parsed_data.keys())}")

                    if 'updates' in parsed_data and 'response' in parsed_data['updates']:
                        response_preview = parsed_data['updates']['response'][:100]
                        print(f"📤 [BACKEND] 响应内容预览: {response_preview}...")

                except Exception as e:
                    print(f"⚠️ [BACKEND] 数据块格式验证失败: {e}")
                    print(f"⚠️ [BACKEND] 数据块内容: {chunk[:200]}...")

                yield chunk

            print(f"✅ [BACKEND] stream_predict完成，总共发送了{chunk_count}个数据块")

        return Response(response=debug_stream_predict(), content_type='application/json', status=200)

    except json.JSONDecodeError as e:
        print(f"❌ [BACKEND] JSON解析错误: {e}")
        print(f"❌ [BACKEND] 原始请求数据: {request.data}")
        error_response = json.dumps({
            "error": "Invalid JSON format",
            "updates": {"response": "请求格式错误：无效的JSON"}
        }, ensure_ascii=False)
        return Response(response=error_response, content_type='application/json', status=400)

    except Exception as e:
        print(f"❌ [BACKEND] 处理请求时发生错误: {e}")
        import traceback
        traceback.print_exc()
        error_response = json.dumps({
            "error": str(e),
            "updates": {"response": f"服务器错误：{str(e)}"}
        }, ensure_ascii=False)
        return Response(response=error_response, content_type='application/json', status=500)
