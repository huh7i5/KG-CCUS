#!/usr/bin/env python3
"""
测试CCUS对话功能
"""

import sys
import os
sys.path.append('server')

def test_ccus_responses():
    """测试CCUS相关问题的回答质量"""
    print("🧪 Testing CCUS-specific responses...")

    try:
        from app.utils.simple_chat import SimpleChatGLM

        model_path = "/fast/zwj/ChatGLM-6B/weights"
        chat_glm = SimpleChatGLM(model_path, memory_optimize=True)

        # 快速加载测试
        chat_glm.load_model()

        # CCUS相关问题测试
        ccus_questions = [
            "什么是CCUS技术？",
            "北京地区适合什么CCUS技术？",
            "CCUS技术的成本如何？",
            "CCUS技术的政策支持情况",
            "CCUS技术有哪些应用案例？",
            "碳捕集技术的工作原理",
            "碳中和目标下CCUS的作用",
        ]

        print("\n📋 CCUS对话测试结果：")
        print("=" * 60)

        for i, question in enumerate(ccus_questions):
            print(f"\n🔍 问题 {i+1}: {question}")
            try:
                for response, _ in chat_glm.stream_chat(question, []):
                    # 检查回答质量
                    is_relevant = any(keyword in response for keyword in ["CCUS", "碳捕集", "碳储存", "碳利用", "二氧化碳"])
                    is_informative = len(response) > 50
                    has_structure = "**" in response or "•" in response or "\n" in response

                    print(f"💬 回答: {response[:150]}...")
                    print(f"📊 质量评估:")
                    print(f"   - 相关性: {'✅' if is_relevant else '❌'}")
                    print(f"   - 信息量: {'✅' if is_informative else '❌'}")
                    print(f"   - 结构化: {'✅' if has_structure else '❌'}")
                    break
            except Exception as e:
                print(f"❌ 回答生成失败: {e}")

    except Exception as e:
        print(f"❌ CCUS测试失败: {e}")

def main():
    print("🚀 开始CCUS智能问答系统测试...")
    test_ccus_responses()
    print("\n✅ CCUS对话测试完成！")

if __name__ == "__main__":
    main()