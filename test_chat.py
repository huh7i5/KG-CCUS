#!/usr/bin/env python3
"""
测试ChatGLM聊天功能
"""

import requests
import json

def test_chat():
    """测试聊天接口"""

    url = "http://localhost:8000/chat"

    # 测试多个场景
    test_cases = [
        {"prompt": "你好", "history": []},
        {"prompt": "什么是知识图谱？", "history": []},
        {"prompt": "再见", "history": []}
    ]

    print("🧪 Testing chat functionality...")

    for i, test_data in enumerate(test_cases, 1):
        print(f"\n--- Test {i} ---")
        print(f"Sending: {test_data['prompt']}")

        try:
            response = requests.post(url, json=test_data, timeout=30)

            if response.status_code == 200:
                print("✅ Chat request successful!")

                # 解析响应
                lines = response.text.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if 'updates' in data and 'response' in data['updates']:
                                print(f"🤖 Response: {data['updates']['response']}")
                        except json.JSONDecodeError:
                            continue
            else:
                print(f"❌ Chat request failed: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_chat()