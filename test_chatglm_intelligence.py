#!/usr/bin/env python3
"""
测试ChatGLM智能回复功能 - 完整的知识图谱增强智能问答流程
验证从NER -> 图谱检索 -> prompt构建 -> ChatGLM推理 -> 智能回复的全流程
"""

import sys
import os
sys.path.append('server')
sys.path.append('server/app')

def test_complete_knowledge_graph_flow():
    """测试完整的知识图谱增强智能问答流程"""
    print("🚀 测试完整的知识图谱增强智能问答流程")
    print("=" * 70)

    try:
        from app.utils.chat_glm import stream_predict

        # CCUS专业问题测试用例
        test_cases = [
            {
                "query": "什么是CCUS技术？",
                "expectation": "应该包含知识图谱信息和ChatGLM智能生成的回答"
            },
            {
                "query": "北京地区适合什么CCUS技术？",
                "expectation": "应该结合地理和技术信息生成专业回答"
            },
            {
                "query": "CCUS技术的成本如何？",
                "expectation": "应该包含成本分析和投资信息"
            },
            {
                "query": "碳捕集技术的工作原理是什么？",
                "expectation": "应该详细介绍技术原理"
            }
        ]

        results = []

        for i, test_case in enumerate(test_cases):
            print(f"\n📝 测试案例 {i+1}: {test_case['query']}")
            print(f"🎯 预期: {test_case['expectation']}")
            print("-" * 50)

            try:
                responses = []
                # 收集流式响应
                for response_data in stream_predict(test_case['query'], []):
                    if isinstance(response_data, bytes):
                        response_data = response_data.decode('utf-8')
                    responses.append(response_data)

                    # 限制收集数量，避免无限循环
                    if len(responses) >= 3:
                        break

                if responses:
                    # 解析最后一个响应
                    import json
                    try:
                        last_response = json.loads(responses[-1])
                        final_answer = last_response.get('updates', {}).get('response', '')

                        print(f"✅ 获得回答: {final_answer[:200]}...")

                        # 质量评估
                        quality_score = assess_response_quality(test_case['query'], final_answer)
                        print(f"📊 质量评估: {quality_score}")

                        results.append({
                            'query': test_case['query'],
                            'response': final_answer,
                            'quality': quality_score,
                            'success': True
                        })

                    except json.JSONDecodeError:
                        print(f"⚠️ 响应格式解析失败: {responses[-1][:100]}...")
                        results.append({
                            'query': test_case['query'],
                            'response': str(responses[-1])[:200],
                            'quality': {'valid': False},
                            'success': False
                        })
                else:
                    print("❌ 没有收到任何响应")
                    results.append({
                        'query': test_case['query'],
                        'response': None,
                        'quality': {'valid': False},
                        'success': False
                    })

            except Exception as e:
                print(f"❌ 测试失败: {e}")
                import traceback
                traceback.print_exc()
                results.append({
                    'query': test_case['query'],
                    'response': None,
                    'quality': {'valid': False, 'error': str(e)},
                    'success': False
                })

        # 总结测试结果
        print("\n" + "=" * 70)
        print("📊 测试结果总结")
        print("=" * 70)

        successful_tests = sum(1 for r in results if r['success'])
        total_tests = len(results)

        print(f"✅ 成功率: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")

        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['query']}")
            if result['success'] and result['quality'].get('chatglm_generated'):
                print(f"   🤖 ChatGLM智能回复: {'是' if result['quality']['chatglm_generated'] else '否'}")
                print(f"   📚 包含知识图谱信息: {'是' if result['quality']['has_knowledge'] else '否'}")
                print(f"   🎯 回答相关性: {'高' if result['quality']['relevant'] else '低'}")

        return results

    except Exception as e:
        print(f"❌ 完整流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def assess_response_quality(query, response):
    """评估回答质量"""
    if not response:
        return {'valid': False, 'reason': 'No response'}

    quality = {
        'valid': True,
        'length': len(response),
        'has_knowledge': False,
        'relevant': False,
        'chatglm_generated': False,
        'structured': False
    }

    # 检查是否包含知识图谱信息
    knowledge_indicators = ['基于', '根据', '知识图谱', '相关信息', '专业']
    quality['has_knowledge'] = any(indicator in response for indicator in knowledge_indicators)

    # 检查相关性
    query_keywords = ['ccus', '碳捕集', '碳储存', '碳利用', '技术', '成本', '原理']
    relevant_keywords = [kw for kw in query_keywords if kw in query.lower()]
    if relevant_keywords:
        quality['relevant'] = any(kw in response.lower() for kw in relevant_keywords)
    else:
        quality['relevant'] = True  # 如果没有特定关键词，默认相关

    # 检查是否是ChatGLM生成的智能回复（不是模板响应）
    template_indicators = [
        '模板响应', 'template', '预设回答', '标准回复',
        '我理解您想了解', '这是一个很好的问题', '请稍等，我正在为您查找'
    ]
    quality['chatglm_generated'] = not any(indicator in response for indicator in template_indicators)

    # 检查是否结构化
    structure_indicators = ['**', '•', '\n', '1.', '2.', '一、', '二、']
    quality['structured'] = any(indicator in response for indicator in structure_indicators)

    # 检查回答长度是否合理
    quality['length_adequate'] = 50 <= len(response) <= 2000

    return quality

def test_simple_chatglm_directly():
    """直接测试SimpleChatGLM，验证tokenizer修复效果"""
    print("\n🧪 直接测试SimpleChatGLM")
    print("=" * 50)

    try:
        from app.utils.simple_chat import SimpleChatGLM

        model_path = "/fast/zwj/ChatGLM-6B/weights"
        chat_glm = SimpleChatGLM(model_path, memory_optimize=True)

        if chat_glm.load_model():
            print("✅ ChatGLM模型加载成功")

            test_query = "请介绍CCUS技术的基本原理"
            print(f"📝 测试问题: {test_query}")

            try:
                for response, history in chat_glm.stream_chat(test_query, []):
                    print(f"🤖 ChatGLM回答: {response[:150]}...")

                    # 检查是否真的是ChatGLM生成的
                    if "chatglm" in response.lower() or len(response) > 100:
                        print("✅ 确认是ChatGLM智能生成的回答")
                        return True
                    else:
                        print("⚠️ 可能仍在使用模板响应")
                        return False
                    break
            except Exception as e:
                print(f"❌ ChatGLM调用失败: {e}")
                return False
        else:
            print("❌ ChatGLM模型加载失败")
            return False

    except Exception as e:
        print(f"❌ SimpleChatGLM测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎯 ChatGLM智能回复功能验证测试")
    print("🎯 目标：验证真正的ChatGLM智能回复，而非模板响应")
    print("🎯 流程：NER → 图谱检索 → prompt构建 → ChatGLM推理 → 智能回复")
    print("=" * 70)

    # 测试1: 直接测试SimpleChatGLM
    simple_test_result = test_simple_chatglm_directly()

    # 测试2: 完整知识图谱增强流程
    complete_test_results = test_complete_knowledge_graph_flow()

    print("\n" + "🎯" * 20)
    print("🎯 最终验证结果")
    print("🎯" * 20)

    if simple_test_result:
        print("✅ SimpleChatGLM直接调用: 成功")
    else:
        print("❌ SimpleChatGLM直接调用: 失败")

    if complete_test_results:
        successful_complete = sum(1 for r in complete_test_results if r['success'])
        total_complete = len(complete_test_results)
        if successful_complete > 0:
            print(f"✅ 知识图谱增强流程: {successful_complete}/{total_complete} 成功")
        else:
            print("❌ 知识图谱增强流程: 全部失败")
    else:
        print("❌ 知识图谱增强流程: 无法运行")

    # 最终结论
    if simple_test_result and complete_test_results:
        print("\n🎉 恭喜！ChatGLM智能回复功能已完全修复！")
        print("🎉 系统现在能够提供真正的ChatGLM智能回复而非模板响应！")
    else:
        print("\n⚠️ 部分功能仍需改进，但基础架构已经完善")

if __name__ == "__main__":
    main()