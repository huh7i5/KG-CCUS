import os
import sys
sys.path.append('server/app')
import json
from opencc import OpenCC
from transformers import AutoTokenizer, AutoModel
from app.utils.image_searcher import ImageSearcher
from app.utils.query_wiki import WikiSearcher
from app.utils.ner import Ner
from app.utils.graph_utils import convert_graph_to_triples, search_node_item, get_entity_details
from app.utils.context_manager import context_manager

model = None
tokenizer = None
init_history = None

ner = Ner()
image_searcher = ImageSearcher()
wiki_searcher = WikiSearcher()
cc = OpenCC('t2s')

def predict(user_input, history=None):
    global model, tokenizer, init_history
    if not history:
        history = init_history
    return model.chat(tokenizer, user_input, history)


def stream_predict(user_input, history=None):
    global model, tokenizer, init_history
    if not history:
        history = init_history

    ref = ""

    # 获取实体
    graph = {}
    entities = []
    entities = ner.get_entities(user_input, etypes=["物体类", "人物类", "地点类", "组织机构类", "事件类", "世界地区类", "术语类"])
    print("entities: ", entities)

    # 使用上下文管理器获取聚焦搜索
    context_graph = context_manager.get_focused_search(entities)
    if context_graph:
        print(f"🎯 Using focused search with {len(context_graph.get('nodes', []))} nodes")

    # 获取实体的三元组和知识内容
    triples = []
    knowledge_content = ""
    for entity in entities:
        entity_graph = search_node_item(entity, graph if graph else None)

        if entity_graph:
            # 合并图谱数据
            if not graph:
                graph = entity_graph
            else:
                # 合并节点
                existing_nodes = {node['name']: node for node in graph['nodes']}
                for node in entity_graph['nodes']:
                    if node['name'] not in existing_nodes:
                        node['id'] = len(graph['nodes'])
                        graph['nodes'].append(node)

                # 合并链接
                for link in entity_graph['links']:
                    if link not in graph['links']:
                        graph['links'].append(link)

                # 合并句子
                for sent in entity_graph['sents']:
                    if sent not in graph['sents']:
                        graph['sents'].append(sent)

            # 提取三元组
            entity_triples = convert_graph_to_triples(entity_graph, entity)
            triples.extend(entity_triples)

            # 提取知识内容
            from app.utils.graph_utils import extract_knowledge_content
            entity_knowledge = extract_knowledge_content(entity_graph, entity)
            if entity_knowledge:
                knowledge_content += f"\n\n【{entity}相关知识】\n{entity_knowledge}"

    # 使用SimpleChatGLM的自然语言处理方法
    if chat_glm and hasattr(chat_glm, '_extract_meaningful_info'):
        # 构建原始参考内容用于处理
        triples_str = ""
        for t in triples[:15]:  # 限制三元组数量
            triples_str += f"({t[0]} {t[1]} {t[2]})；"

        raw_ref = ""
        if triples_str:
            raw_ref += f"三元组信息：{triples_str}；"
        if knowledge_content:
            raw_ref += knowledge_content

        # 使用自然语言处理转换
        meaningful_info = chat_glm._extract_meaningful_info(raw_ref, user_input)
        if meaningful_info:
            ref += meaningful_info
        elif knowledge_content:
            ref += knowledge_content
    else:
        # 回退到原有方式
        triples_str = ""
        for t in triples[:15]:  # 限制三元组数量
            triples_str += f"({t[0]} {t[1]} {t[2]})；"

        if triples_str:
            ref += f"三元组信息：{triples_str}；"

        if knowledge_content:
            ref += knowledge_content


    image = image_searcher.search(user_input)

    for ent in entities + [user_input]:
        wiki = wiki_searcher.search(ent)
        if wiki is not None:
            break

    # 将Wikipedia搜索到的繁体转为简体
    if wiki:
        ref += cc.convert(wiki.summary)
        wiki = {
            "title": cc.convert(wiki.title),
            "summary": cc.convert(wiki.summary),
        }
        print(wiki)
    else:
        wiki = {
            "title": "无相关信息",
            "summary": "暂无相关描述",
        }

    if model is not None:
        if ref:
            chat_input = f"\n===参考资料===：\n{ref}；\n\n根据上面资料，用简洁且准确的话回答下面问题：\n{user_input}"
        else:
            chat_input = user_input

        clean_history = []
        for user_msg, response in history:
            # 清理用户输入，移除参考资料部分
            if "===参考资料===" in user_msg:
                clean_user_input = user_msg.split("===参考资料===")[0].strip()
                if "根据上面资料，用简洁且准确的话回答下面问题：" in user_msg:
                    clean_user_input = user_msg.split("根据上面资料，用简洁且准确的话回答下面问题：")[1].strip()
            else:
                clean_user_input = user_msg
            clean_history.append((clean_user_input, response))

        print("chat_input: ", chat_input)

        # 使用新的chat_glm实例或原有方式
        if chat_glm and chat_glm.loaded:
            for response, raw_history in chat_glm.stream_chat(chat_input, clean_history):
                # 清理返回的历史记录，确保用户看到的是原始问题而不是带参考资料的query
                clean_return_history = []
                for h_q, h_r in raw_history:
                    if "===参考资料===" in h_q:
                        if "根据上面资料，用简洁且准确的话回答下面问题：" in h_q:
                            clean_q = h_q.split("根据上面资料，用简洁且准确的话回答下面问题：")[1].strip()
                        else:
                            clean_q = h_q.split("===参考资料===")[0].strip()
                    else:
                        clean_q = h_q
                    clean_return_history.append((clean_q, h_r))

                updates = {
                    "query": user_input,  # 使用原始用户输入，而不是chat_input
                    "response": response
                }

                # 更新上下文
                context_manager.update_context(user_input, entities, graph)

                # 获取实体详细信息
                entity_details = []
                for entity in entities[:3]:  # 限制实体数量
                    details = get_entity_details(entity, graph)
                    if details:
                        entity_details.append(details)

                # 获取建议问题
                suggestions = context_manager.suggest_related_questions(entities)

                # 获取对话摘要
                conversation_summary = context_manager.get_conversation_summary()

                result = {
                    "history": clean_return_history,
                    "updates": updates,
                    "image": image,
                    "graph": graph,
                    "wiki": wiki,
                    "entity_details": entity_details,
                    "suggestions": suggestions,
                    "conversation_summary": conversation_summary
                }
                yield json.dumps(result, ensure_ascii=False).encode('utf8') + b'\n'
        elif model is not None:
            for response, history in model.stream_chat(tokenizer, chat_input, clean_history):
                updates = {}
                for query, response in history:
                    updates["query"] = query
                    updates["response"] = response

                # 更新上下文
                context_manager.update_context(user_input, entities, graph)

                # 获取实体详细信息和建议
                entity_details = []
                for entity in entities[:3]:
                    details = get_entity_details(entity, graph)
                    if details:
                        entity_details.append(details)

                suggestions = context_manager.suggest_related_questions(entities)
                conversation_summary = context_manager.get_conversation_summary()

                result = {
                    "history": history,
                    "updates": updates,
                    "image": image,
                    "graph": graph,
                    "wiki": wiki,
                    "entity_details": entity_details,
                    "suggestions": suggestions,
                    "conversation_summary": conversation_summary
                }
                yield json.dumps(result, ensure_ascii=False).encode('utf8') + b'\n'
        else:
            # 简单回复模式
            updates = {
                "query": user_input,
                "response": "模型加载中，请稍后再试"
            }

            # 更新上下文
            context_manager.update_context(user_input, entities, graph)

            # 获取实体详细信息和建议
            entity_details = []
            for entity in entities[:3]:
                print(f"🔍 Getting details for entity: {entity}")
                details = get_entity_details(entity, graph)
                if details:
                    entity_details.append(details)
                    print(f"📋 Entity details for {entity}: {details['total_connections']} connections")
                else:
                    print(f"❌ No details found for entity: {entity}")

            suggestions = context_manager.suggest_related_questions(entities)
            conversation_summary = context_manager.get_conversation_summary()

            print(f"🔢 Generated {len(entity_details)} entity details, {len(suggestions)} suggestions")

            result = {
                "history": history,
                "updates": updates,
                "image": image,
                "graph": graph,
                "wiki": wiki,
                "entity_details": entity_details,
                "suggestions": suggestions,
                "conversation_summary": conversation_summary
            }
            yield json.dumps(result, ensure_ascii=False).encode('utf8') + b'\n'

    else:
        updates = {
            "query": user_input,
            "response": "模型加载中，请稍后再试"
        }

        # 更新上下文
        context_manager.update_context(user_input, entities, graph)

        # 获取实体详细信息和建议
        entity_details = []
        for entity in entities[:3]:
            print(f"🔍 Getting details for entity: {entity}")
            details = get_entity_details(entity, graph)
            if details:
                entity_details.append(details)
                print(f"📋 Entity details for {entity}: {details['total_connections']} connections")
            else:
                print(f"❌ No details found for entity: {entity}")

        suggestions = context_manager.suggest_related_questions(entities)
        conversation_summary = context_manager.get_conversation_summary()

        print(f"🔢 Generated {len(entity_details)} entity details, {len(suggestions)} suggestions")

        result = {
            "history": history,
            "updates": updates,
            "image": image,
            "graph": graph,
            "wiki": wiki,
            "entity_details": entity_details,
            "suggestions": suggestions,
            "conversation_summary": conversation_summary
        }
        yield json.dumps(result, ensure_ascii=False).encode('utf8') + b'\n'

# 全局ChatGLM实例
chat_glm = None

# 加载模型
def start_model():
    global model, tokenizer, init_history, chat_glm

    # 检查模型路径
    model_path = "/fast/zwj/ChatGLM-6B/weights"

    if os.path.exists(model_path) and os.listdir(model_path):
        # 使用新的简单加载器
        from app.utils.simple_chat import SimpleChatGLM
        chat_glm = SimpleChatGLM(model_path)

        if chat_glm.load_model():
            # 兼容原有接口
            model = chat_glm.model
            tokenizer = chat_glm.tokenizer
            init_history = []
            print("✅ ChatGLM-6B ready for chat!")
        else:
            print("❌ Failed to load ChatGLM-6B")
            model = None
            tokenizer = None
            init_history = []
            chat_glm = None
    else:
        print("Warning: ChatGLM-6B model weights not found at /fast/zwj/ChatGLM-6B/weights")
        print("Using simple response mode. To enable full chat functionality:")
        print("1. Run: python3 download_model.py")
        print("2. Or download model manually to: /fast/zwj/ChatGLM-6B/weights")

        model = None
        tokenizer = None
        init_history = []
        chat_glm = None