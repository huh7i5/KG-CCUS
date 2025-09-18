#!/usr/bin/env python3
"""
简单的ChatGLM API测试脚本
"""

import requests
import json
import time

def test_chat_api():
    """测试聊天API"""

    # 测试后端连接
    try:
        response = requests.get('http://localhost:8000/')
        print(f"✅ 后端连接测试: {response.json()}")
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return

    # 测试知识图谱API
    try:
        response = requests.get('http://localhost:8000/graph/')
        data = response.json()
        nodes_count = len(data.get('data', {}).get('nodes', []))
        print(f"✅ 知识图谱API测试: 加载了 {nodes_count} 个节点")
    except Exception as e:
        print(f"❌ 知识图谱API失败: {e}")
        return

    # 测试聊天功能
    print("\n🤖 测试聊天功能...")

    test_questions = [
        "你好",
        "什么是舰艇损管？",
        "潜水技术有哪些？"
    ]

    for question in test_questions:
        print(f"\n👤 用户: {question}")

        try:
            chat_data = {
                "prompt": question,
                "history": []
            }

            response = requests.post(
                'http://localhost:8000/chat/',
                data=json.dumps(chat_data),
                headers={'Content-Type': 'application/json'},
                stream=True,
                timeout=30
            )

            print("🤖 ChatKG: ", end="", flush=True)

            # 处理流式响应
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'updates' in data and 'response' in data['updates']:
                            response_text = data['updates']['response']
                            if response_text != full_response:
                                print(response_text[len(full_response):], end="", flush=True)
                                full_response = response_text
                    except json.JSONDecodeError:
                        continue

            print()  # 换行

        except Exception as e:
            print(f"❌ 聊天API失败: {e}")
            break

        time.sleep(1)  # 避免请求过快

if __name__ == "__main__":
    print("🚀 开始测试知识图谱聊天系统...")
    test_chat_api()
    print("\n✅ 测试完成！")