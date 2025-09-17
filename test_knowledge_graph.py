#!/usr/bin/env python3
"""
测试知识图谱集成功能
"""

import requests
import json

def test_knowledge_graph_integration():
    """测试知识图谱集成"""

    url = "http://localhost:8000/chat"

    # 测试知识图谱相关的问题
    test_cases = [
        {"prompt": "灭火器", "history": []},
        {"prompt": "潜水器", "history": []},
        {"prompt": "船舶", "history": []},
        {"prompt": "维修", "history": []}
    ]

    print("🧪 Testing Knowledge Graph Integration...")

    for i, test_data in enumerate(test_cases, 1):
        print(f"\n--- Knowledge Graph Test {i} ---")
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

                            # 检查是否有知识图谱信息
                            if 'graph' in data and data['graph']:
                                print(f"🕸️ Knowledge Graph: Found {len(data['graph'])} nodes")

                            if 'wiki' in data and data['wiki'] and data['wiki'].get('title') != '无相关信息':
                                print(f"📚 Wikipedia: {data['wiki']['title']}")
                                print(f"📖 Summary: {data['wiki']['summary'][:100]}...")

                        except json.JSONDecodeError:
                            continue
            else:
                print(f"❌ Chat request failed: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_knowledge_graph_integration()