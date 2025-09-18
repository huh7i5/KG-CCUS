#!/usr/bin/env python3
"""
测试改进后的回答质量
"""

import requests
import json
import time

def test_improved_chat():
    """测试改进后的聊天质量"""

    print("🧪 测试改进后的回答质量...")

    test_questions = [
        "我需要去潜水需要什么装备",
        "舰艇发生火灾怎么办？",
        "什么是损管？",
        "潜水时应该注意什么？",
        "舰艇损管的基本原则是什么？"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"🔍 测试问题 {i}: {question}")
        print(f"{'='*60}")

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
                timeout=60
            )

            print("🤖 ChatKG 回答:", end="", flush=True)

            # 处理流式响应
            full_response = ""
            has_content = False

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'updates' in data and 'response' in data['updates']:
                            response_text = data['updates']['response']
                            if response_text != full_response:
                                new_content = response_text[len(full_response):]
                                print(new_content, end="", flush=True)
                                full_response = response_text
                                has_content = True
                    except json.JSONDecodeError:
                        continue

            if not has_content:
                print(" [无响应]")

            print("\n")  # 换行

            # 分析回答质量
            if full_response:
                print(f"📊 回答分析:")
                print(f"  - 长度: {len(full_response)} 字符")

                # 检查是否还包含原始的知识图谱格式
                if "【" in full_response and "】" in full_response:
                    print("  - ⚠️  仍包含知识图谱格式标记")
                else:
                    print("  - ✅ 格式已优化")

                # 检查是否直接回答了问题
                if question.replace("？", "").replace("?", "") in full_response:
                    print("  - ✅ 回答相关性较高")
                else:
                    print("  - ⚠️  回答相关性需要改进")

                # 检查语言自然度
                if "三元组信息" in full_response or "【相关关系】" in full_response:
                    print("  - ❌ 仍包含技术术语，不够自然")
                else:
                    print("  - ✅ 语言表达自然")

        except Exception as e:
            print(f"❌ 测试失败: {e}")

        time.sleep(2)  # 避免请求过快

    print(f"\n{'='*60}")
    print("🎯 测试完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_improved_chat()