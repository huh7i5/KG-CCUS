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

class KnowledgeGraphQA:
    """CCUS知识图谱智能问答系统 - 按照流程图实现"""

    def __init__(self):
        self.ner = Ner()
        self.image_searcher = ImageSearcher()
        self.wiki_searcher = WikiSearcher()
        self.cc = OpenCC('t2s')

    def named_entity_recognition(self, user_input):
        """步骤1: 命名实体识别模型"""
        entities = self.ner.get_entities(
            user_input,
            etypes=["物体类", "人物类", "地点类", "组织机构类", "事件类", "世界地区类", "术语类"]
        )
        return entities

    def graph_search(self, entities):
        """步骤2: 图谱检索 - 在领域知识图谱中检索相关实体"""
        graph_data = {}
        subgraph_data = {}
        triples = []

        for entity in entities:
            entity_graph = search_node_item(entity, graph_data if graph_data else None)

            if entity_graph and entity_graph.get('nodes'):
                # 合并图谱数据
                if not graph_data:
                    graph_data = entity_graph
                else:
                    # 合并节点
                    existing_nodes = {node['name']: node for node in graph_data['nodes']}
                    for node in entity_graph['nodes']:
                        if node['name'] not in existing_nodes:
                            node['id'] = len(graph_data['nodes'])
                            graph_data['nodes'].append(node)

                    # 合并链接
                    for link in entity_graph['links']:
                        if link not in graph_data['links']:
                            graph_data['links'].append(link)

                    # 合并句子
                    for sent in entity_graph['sents']:
                        if sent not in graph_data['sents']:
                            graph_data['sents'].append(sent)

                # 提取三元组
                entity_triples = convert_graph_to_triples(entity_graph, entity)
                triples.extend(entity_triples)

                # 构建子图谱
                subgraph_data[entity] = {
                    'graph': entity_graph,
                    'triples': entity_triples
                }

        return {
            'full_graph': graph_data,
            'subgraphs': subgraph_data,
            'triples': triples
        }

    def external_knowledge_search(self, entities, user_input):
        """步骤3: 外部知识检索 - 从Wikipedia等外部数据库检索"""
        external_knowledge = {}

        # 图片搜索
        image_result = self.image_searcher.search(user_input)
        if image_result:
            external_knowledge['image'] = image_result

        # Wikipedia搜索
        wiki_result = None
        for entity in entities + [user_input]:
            wiki = self.wiki_searcher.search(entity)
            if wiki is not None:
                wiki_result = {
                    "title": self.cc.convert(wiki.title),
                    "summary": self.cc.convert(wiki.summary),
                }
                break

        if not wiki_result:
            wiki_result = {
                "title": "无相关信息",
                "summary": "暂无相关描述",
            }

        external_knowledge['wiki'] = wiki_result
        return external_knowledge

    def structured_processing(self, graph_results, external_knowledge, entities):
        """步骤4: 结构化处理 - 整合多源信息"""
        structured_info = {
            'entities': entities,
            'relations': [],
            'knowledge_text': "",
            'context_info': {}
        }

        # 处理图谱三元组信息
        if graph_results['triples']:
            relation_groups = {}
            for triple in graph_results['triples'][:10]:  # 限制数量
                if len(triple) >= 3:
                    relation = triple[1]
                    if relation not in relation_groups:
                        relation_groups[relation] = []
                    relation_groups[relation].append((triple[0], triple[2]))

            # 转换为结构化关系描述
            for relation, pairs in relation_groups.items():
                for subject, obj in pairs[:3]:  # 每种关系最多3个例子
                    structured_info['relations'].append({
                        'subject': subject,
                        'predicate': relation,
                        'object': obj,
                        'description': f"{subject}与{obj}的关系是{relation}"
                    })

        # 处理图谱知识内容
        if graph_results.get('subgraphs'):
            knowledge_parts = []
            for entity, subgraph in graph_results['subgraphs'].items():
                from app.utils.graph_utils import extract_knowledge_content
                entity_knowledge = extract_knowledge_content(subgraph['graph'], entity)
                if entity_knowledge:
                    knowledge_parts.append(f"{entity}: {entity_knowledge}")

            if knowledge_parts:
                structured_info['knowledge_text'] = "; ".join(knowledge_parts)

        # 整合外部知识
        if external_knowledge.get('wiki') and external_knowledge['wiki']['summary'] != "暂无相关描述":
            wiki_summary = external_knowledge['wiki']['summary'][:200]  # 限制长度
            structured_info['context_info']['wikipedia'] = wiki_summary

        return structured_info

    def build_prompt(self, user_input, structured_info):
        """步骤5: 构建prompt - 为对话语言模型构建上下文"""
        prompt_parts = []

        # 添加实体信息
        if structured_info['entities']:
            entities_str = "、".join(structured_info['entities'][:5])
            prompt_parts.append(f"相关实体: {entities_str}")

        # 添加关系信息
        if structured_info['relations']:
            relations_str = "; ".join([rel['description'] for rel in structured_info['relations'][:5]])
            prompt_parts.append(f"知识关系: {relations_str}")

        # 添加知识内容
        if structured_info['knowledge_text']:
            knowledge_str = structured_info['knowledge_text'][:300]  # 限制长度
            prompt_parts.append(f"背景知识: {knowledge_str}")

        # 添加外部上下文
        if structured_info['context_info'].get('wikipedia'):
            wiki_str = structured_info['context_info']['wikipedia']
            prompt_parts.append(f"参考信息: {wiki_str}")

        if prompt_parts:
            context = "\n".join(prompt_parts)
            prompt = f"""基于以下知识信息回答用户问题:

{context}

用户问题: {user_input}

请基于上述信息提供准确、专业的回答。如果信息不足，请基于CCUS领域常识进行合理回答。"""
        else:
            prompt = user_input

        return prompt

    def generate_response(self, prompt, history, chat_glm_model=None):
        """步骤6: 对话语言模型生成回答"""
        if chat_glm_model and chat_glm_model.loaded:
            # 使用ChatGLM模型
            for response, updated_history in chat_glm_model.stream_chat(prompt, history):
                # 清理响应中的prompt内容
                cleaned_response = self._clean_response(response)
                yield cleaned_response, updated_history
        else:
            # 简单模式回答
            response = self._generate_simple_response(prompt)
            updated_history = history + [(prompt, response)]
            yield response, updated_history

    def _clean_response(self, response):
        """清理模型响应中的prompt内容"""
        if not response:
            return response

        # 移除明显的prompt片段
        clean_patterns = [
            "基于以下知识信息回答用户问题:",
            "用户问题:",
            "请基于上述信息提供准确、专业的回答",
            "如果信息不足，请基于CCUS领域常识进行合理回答"
        ]

        cleaned = response
        for pattern in clean_patterns:
            if pattern in cleaned:
                parts = cleaned.split(pattern)
                if len(parts) > 1:
                    cleaned = parts[-1].strip()

        return cleaned if len(cleaned.strip()) > 10 else response

    def _generate_simple_response(self, prompt):
        """生成简单回答（当没有ChatGLM模型时）"""
        if "ccus" in prompt.lower() or "碳捕集" in prompt or "二氧化碳" in prompt:
            return "CCUS是碳捕集、利用与储存技术，是应对气候变化的重要技术手段。该技术通过捕集工业排放的二氧化碳，进行资源化利用或安全储存。"
        else:
            return "根据知识图谱信息，我为您提供相关的CCUS技术领域回答。"

# 全局实例
kg_qa_system = KnowledgeGraphQA()
chat_glm = None

def predict(user_input, history=None):
    """兼容原有接口"""
    global model, tokenizer, init_history
    if not history:
        history = init_history
    return model.chat(tokenizer, user_input, history)

def stream_predict(user_input, history=None):
    """主要的流式预测函数 - 按照流程图实现"""
    global model, tokenizer, init_history, chat_glm
    if not history:
        history = init_history or []

    # 步骤1: 命名实体识别
    entities = kg_qa_system.named_entity_recognition(user_input)

    # 步骤2: 图谱检索
    graph_results = kg_qa_system.graph_search(entities)

    # 步骤3: 外部知识检索
    external_knowledge = kg_qa_system.external_knowledge_search(entities, user_input)

    # 步骤4: 结构化处理
    structured_info = kg_qa_system.structured_processing(graph_results, external_knowledge, entities)

    # 步骤5: 构建prompt
    prompt = kg_qa_system.build_prompt(user_input, structured_info)

    # 更新上下文管理器
    context_manager.update_context(user_input, entities, graph_results['full_graph'])

    # 步骤6: 对话语言模型生成回答
    for response, updated_history in kg_qa_system.generate_response(prompt, history, chat_glm):
        # 构建返回结果
        result = {
            "history": updated_history,
            "updates": {
                "query": user_input,
                "response": response
            },
            "image": external_knowledge.get('image'),
            "graph": graph_results['full_graph'] if graph_results['full_graph'] and len(graph_results['full_graph'].get('nodes', [])) <= 50 else None,
            "wiki": external_knowledge['wiki']
        }
        yield json.dumps(result, ensure_ascii=False).encode('utf8') + b'\n'

def start_model():
    """加载模型"""
    global model, tokenizer, init_history, chat_glm

    print("🚀 Starting CCUS Knowledge Graph QA System...")

    # 检查模型路径
    model_path = "/fast/zwj/ChatGLM-6B/weights"

    if os.path.exists(model_path) and os.listdir(model_path):
        try:
            from app.utils.simple_chat import SimpleChatGLM

            print(f"📁 Loading ChatGLM model from: {model_path}")
            chat_glm = SimpleChatGLM(model_path, memory_optimize=True)

            if chat_glm.load_model():
                model = chat_glm.model
                tokenizer = chat_glm.tokenizer
                init_history = []
                print("✅ ChatGLM-6B loaded successfully!")
            else:
                print("❌ Failed to load ChatGLM-6B")
                model = None
                tokenizer = None
                init_history = []
                chat_glm = None
        except Exception as e:
            print(f"❌ Error loading ChatGLM: {e}")
            model = None
            tokenizer = None
            init_history = []
            chat_glm = None
    else:
        print("⚠️  ChatGLM model not found, using simple response mode")
        model = None
        tokenizer = None
        init_history = []
        chat_glm = None

    print("🎯 CCUS Knowledge Graph QA System ready!")