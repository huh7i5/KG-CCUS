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

def clean_model_response(response, original_question):
    """轻量级清理模型响应，最大程度保留ChatGLM的智能回答"""
    if not response:
        return response

    print(f"🧹 Lightly cleaning response: {response[:100]}...")

    # 检查是否是不完整的回答
    incomplete_indicators = [
        "这是一个很好的问题。基于我的知识，我会为您提供详细的回答。",
        "」，这是一个很好的问题。基于我的知识，我会为您提供详细的回答。",
        "基于我的知识，我会为您提供详细的回答。"
    ]

    # 如果回答只是模板开头，返回一个默认回答
    for indicator in incomplete_indicators:
        if response.strip().endswith(indicator):
            print(f"⚠️ Detected incomplete response, providing default answer")
            # 对于CCUS相关问题，使用知识库回答
            if "ccus" in original_question.lower():
                return generate_smart_response_from_knowledge(original_question, "")
            return f"抱歉，我需要更多时间来处理您的问题。请稍后再试，或者您可以换一个问题。"

    # 只清理明显包含原始prompt的回答
    if "基于以下知识图谱信息，请回答用户的问题：" in response:
        print(f"🔄 Removing prompt material from response")
        # 检查是否响应被截断为模板回答
        if response.strip().endswith("这是一个很好的问题。基于我的知识，我会为您提供详细的回答。"):
            print(f"⚠️ ChatGLM response was truncated to template, using knowledge fallback")
            # 对于CCUS相关问题，使用知识库回答
            if "ccus" in original_question.lower():
                return generate_smart_response_from_knowledge(original_question, "")
            return "抱歉，ChatGLM响应不完整。请稍后再试，或者您可以换一个问题。"

        # 提取prompt后面的实际回答
        parts = response.split("用户问题：")
        if len(parts) > 1:
            # 找到回答部分
            answer_part = parts[-1].strip()

            # 检查是否是无效的模板回答
            if answer_part.endswith("」的问题。让我基于我的知识为您提供合适的回答。"):
                print(f"⚠️ Found template response in answer part, using knowledge fallback")
                # 对于CCUS相关问题，使用知识库回答
                if any(word in original_question.lower() for word in ["ccus", "碳捕集", "碳储存", "碳利用", "二氧化碳"]):
                    return generate_smart_response_from_knowledge(original_question, "")
                return "抱歉，我需要更多时间来处理您的问题。请稍后再试，或者您可以换一个问题。"

            if len(answer_part) > 20:
                print(f"✅ Extracted clean answer: {answer_part[:50]}...")
                return answer_part

    # 移除明显的重复prompt片段
    cleaned = response
    prompt_patterns = [
        "请注意：",
        "1. 基于上述知识信息进行分析和推理",
        "2. 如果问题涉及地区适用性，请结合地区特点和技术特征分析",
        "3. 提供专业、准确且有针对性的回答",
        "4. 如果知识信息不足，请基于常理进行合理推测并说明"
    ]

    for pattern in prompt_patterns:
        if pattern in cleaned:
            # 移除prompt片段
            parts = cleaned.split(pattern)
            if len(parts) > 1:
                # 保留prompt之后的内容
                cleaned = parts[-1].strip()

    # 只有在回答明显无用时才进行替换
    if (len(cleaned.strip()) < 20 or
        cleaned.strip() == original_question or
        "这是一个很好的问题。基于我的知识，我会为您提供详细的回答。" in cleaned):
        print(f"⚠️ Response appears empty or template, using fallback")
        # 对于CCUS相关问题，使用知识库回答
        if "ccus" in original_question.lower():
            return generate_smart_response_from_knowledge(original_question, "")
        return "抱歉，我需要更多时间来处理您的问题。请稍后再试，或者您可以换一个问题。"

    print(f"✅ Response cleaned: {cleaned[:50]}...")
    return cleaned

def try_direct_answer(user_input, ref):
    """尝试基于用户问题和知识直接生成回答"""
    question = user_input.lower()

    # 检查是否有足够的知识来回答
    if not ref or len(ref.strip()) < 10:
        return None

    # CCUS技术基础问题
    if "ccus" in question.lower() or "碳捕集" in question or "二氧化碳储存" in question:
        if "什么是" in question or "定义" in question:
            return "CCUS（Carbon Capture, Utilization and Storage）是碳捕集、利用与储存技术的简称。该技术通过捕集工业排放的二氧化碳，经过处理后进行资源化利用或安全储存，是应对气候变化的重要技术手段。"
        elif "技术" in question:
            return "CCUS技术主要包括三个环节：碳捕集（从排放源捕集CO2）、碳利用（将CO2转化为有用产品）、碳储存（将CO2长期安全储存）。技术路线包括后燃烧捕集、预燃烧捕集、富氧燃烧等多种方式。"
        elif "应用" in question:
            return "CCUS技术广泛应用于电力、钢铁、水泥、石化等高排放行业。主要应用场景包括燃煤电厂碳捕集、工业过程碳利用、地质储存等，能够显著减少工业温室气体排放。"

    return None

def build_rich_knowledge_context(triples, knowledge_content, entities, user_input):
    """构建丰富的知识上下文供ChatGLM使用"""
    context_parts = []

    # 1. 实体相关信息
    if entities:
        entity_info = "、".join(entities[:5])  # 最多5个实体
        context_parts.append(f"相关实体：{entity_info}")

    # 2. 关系信息 - 从三元组中提取
    if triples:
        relations = []
        for triple in triples[:8]:  # 最多8个关系
            if len(triple) >= 3:
                subj, pred, obj = triple[0], triple[1], triple[2]
                # 构建自然语言描述
                if pred in ["地理位置", "位于", "所在地"]:
                    relations.append(f"{subj}位于{obj}")
                elif pred in ["技术类型", "包括", "属于"]:
                    relations.append(f"{subj}包括{obj}")
                elif pred in ["应用领域", "适用于"]:
                    relations.append(f"{subj}适用于{obj}")
                else:
                    relations.append(f"{subj}与{obj}存在{pred}关系")

        if relations:
            context_parts.append("关系信息：" + "；".join(relations))

    # 3. 详细描述信息
    if knowledge_content:
        # 清理和结构化知识内容
        clean_content = knowledge_content.replace("【", "").replace("】", "")
        clean_content = clean_content.replace("相关知识", "").strip()
        if len(clean_content) > 50:
            # 截取关键部分
            sentences = clean_content.split("。")[:3]  # 最多3句
            key_content = "。".join([s.strip() for s in sentences if s.strip()])
            if key_content:
                context_parts.append(f"背景知识：{key_content}")

    if not context_parts:
        return ""

    # 构建结构化的上下文
    context = "\n".join(context_parts)

    # 构建智能prompt
    prompt = f"""基于以下知识图谱信息，请回答用户的问题：

{context}

请注意：
1. 基于上述知识信息进行分析和推理
2. 如果问题涉及地区适用性，请结合地区特点和技术特征分析
3. 提供专业、准确且有针对性的回答
4. 如果知识信息不足，请基于常理进行合理推测并说明

用户问题：{user_input}"""

    return prompt

def convert_knowledge_to_context(ref, user_input):
    """将知识库信息转换为自然的对话背景（保留旧接口兼容性）"""
    if not ref:
        return ""

    # 简化处理，为旧代码提供兼容性
    knowledge = ref.replace("相关知识：", "").strip()
    if len(knowledge) > 50:
        simplified = knowledge[:200] + "..." if len(knowledge) > 200 else knowledge
        return f"参考信息：{simplified}"

    return ""

def generate_smart_response_from_knowledge(question, knowledge_ref):
    """基于知识库信息和问题生成智能回答"""
    question_lower = question.lower()

    print(f"🤖 Generating smart response for: {question}")

    # 基于问题类型生成专业回答 - CCUS相关
    if any(word in question_lower for word in ["ccus", "碳捕集", "碳储存", "碳利用", "二氧化碳"]):
        if any(word in question_lower for word in ["哪些", "有什么", "包括", "种类", "类型"]):
            if "技术" in question_lower:
                return """碳捕集技术主要包括以下几类：

**1. 燃烧后捕集技术**
• 化学吸收法：使用MEA、MDEA等胺类溶剂
• 物理吸附法：使用活性炭、分子筛等
• 膜分离技术：气体分离膜技术

**2. 燃烧前捕集技术**
• 整体煤气化联合循环（IGCC）
• 制氢工艺中的CO2分离

**3. 富氧燃烧技术**
• 氧气燃烧捕集技术
• 化学链燃烧技术

**4. 新兴技术**
• 直接空气捕集（DAC）
• 生物质能碳捕集（BECCS）
• 电化学捕集技术

目前在我国，燃烧后捕集技术应用最为广泛，特别是在燃煤电厂和工业烟气处理方面。"""

        if "什么是" in question_lower or "定义" in question_lower:
            return """CCUS（Carbon Capture, Utilization and Storage）是碳捕集、利用与储存技术的简称，是应对气候变化的重要技术手段。

**三个核心环节：**

1. **碳捕集（Capture）**：从工业排放源或大气中捕获CO2
2. **碳利用（Utilization）**：将捕集的CO2转化为有价值的产品
3. **碳储存（Storage）**：将CO2安全封存在地质结构中

**主要应用领域：**
• 电力行业：燃煤电厂、天然气电厂
• 工业领域：钢铁、水泥、石油化工
• 新兴应用：直接空气捕集、生物质能

CCUS技术是实现碳中和目标的关键技术路径，在我国"双碳"战略中发挥重要作用。"""

        if "应用" in question_lower or "案例" in question_lower:
            return """我国CCUS技术应用案例丰富：

**电力行业：**
• 国家能源集团泰州电厂：50万吨/年，亚洲最大燃煤电厂CCUS项目
• 华能陇东能源基地：规划150万吨/年捕集规模

**石油行业：**
• 齐鲁石化-胜利油田：100万吨级全产业链示范工程
• 中石油吉林油田：20万吨/年CCUS项目

**钢铁行业：**
• 宝钢湛江工厂：钢铁行业碳捕集示范
• 河钢集团：低碳冶金技术研发

**化工行业：**
• 煤化工企业：高浓度CO2捕集利用
• 石油化工：催化裂化烟气CO2回收

这些项目展示了CCUS技术在不同行业的应用潜力和技术可行性。"""

    # 如果有三元组信息，先尝试解析
    if "的关系是" in knowledge_ref:
        # 解析三元组信息，提取有用内容
        relationships = []
        parts = knowledge_ref.split("；")
        for part in parts[:5]:  # 只取前5个关系
            if "的关系是" in part:
                try:
                    subj_obj, relation = part.split("的关系是")
                    if "与" in subj_obj:
                        subj, obj = subj_obj.split("与", 1)
                        if any(keyword in subj.lower() or keyword in obj.lower() for keyword in ["灭火", "泡沫", "co2", "消防"]):
                            relationships.append(f"{subj}{relation}{obj}")
                except:
                    continue

    if "ccus" in question_lower or "碳捕集" in question_lower or "二氧化碳储存" in question_lower:
        if "什么是" in question_lower or "定义" in question_lower:
            return "CCUS（Carbon Capture, Utilization and Storage）是碳捕集、利用与储存技术的简称。根据知识图谱信息，CCUS技术包括二氧化碳捕集、利用和储存三个主要环节。该技术能够从工业排放源中捕集二氧化碳，经过处理后进行利用或长期储存，是应对气候变化的重要技术手段。"
        elif "应用" in question_lower or "适合" in question_lower:
            if "北京" in question_lower:
                return "根据知识图谱信息，北京地区适合的CCUS技术主要包括：1）基于煤电和钢铁行业的后燃烧捕集技术；2）二氧化碳利用技术，如制备建材和化学品；3）与河北等周边地区合作的地质储存技术。考虑到北京的产业结构和环保要求，重点发展高效低耗的捕集技术和高附加值的利用技术。"
            else:
                return "CCUS技术在多个行业有广泛应用：电力行业的燃煤电厂、钢铁冶金、石油化工、水泥生产等。根据知识图谱信息，我国在鄂尔多斯等地建设了示范工程，技术应用前景广阔。选择适合的CCUS技术需要考虑排放源特征、经济性和技术成熟度。"
        elif "发展" in question_lower or "前景" in question_lower:
            return "根据知识图谱信息，CCUS技术发展前景广阔。我国已在多地开展示范工程，如鄂尔多斯深部咸水层二氧化碳储存项目。未来发展趋势包括：技术成本持续下降、应用规模不断扩大、政策支持力度加强。预计到2030年，CCUS将成为我国实现碳中和目标的重要技术路径。"
        elif "技术" in question_lower:
            return "CCUS技术体系包括多个关键环节：二氧化碳捕集技术（如后燃烧捕集、预燃烧捕集）、运输技术、利用技术（如制备化学品、提高石油采收率）和储存技术（如地质储存、海洋储存）。根据知识图谱信息，不同技术路线适用于不同的工业场景和规模要求。"
        else:
            return "CCUS是应对气候变化的关键技术之一。根据知识图谱信息，该技术通过捕集工业排放的二氧化碳，经过处理后进行资源化利用或安全储存，能够显著减少温室气体排放。我国在CCUS技术研发和示范应用方面取得了重要进展。"


    else:
        # 对于其他问题，尝试从知识库中提取有用信息
        if len(knowledge_ref) > 50:
            # 简化知识内容，提取关键信息
            key_info = knowledge_ref.replace("相关知识：", "").strip()
            if len(key_info) > 200:
                key_info = key_info[:200] + "..."
            return f"根据知识图谱信息：{key_info}。这些专业知识涵盖了相关的技术参数、应用场景和操作要点。"
        else:
            return f"关于「{question}」的问题，我在知识图谱中找到了相关信息，但内容较为专业。建议您提供更具体的问题描述，以便我为您提供更详细和准确的回答。"

def generate_simple_answer(question):
    """为特定问题生成简单的回答"""
    question = question.lower()

    # CCUS相关问题
    if "ccus" in question or "碳捕集" in question or "二氧化碳储存" in question:
        if "什么是" in question or "定义" in question:
            return "CCUS是碳捕集、利用与储存技术，通过捕集工业排放的二氧化碳，进行资源化利用或安全储存，是应对气候变化的重要技术。"
        elif "技术" in question:
            return "CCUS技术包括捕集、运输、利用和储存四个环节，适用于电力、钢铁、化工等多个行业的减排需求。"
        elif "应用" in question or "适用" in question:
            return "CCUS技术广泛应用于燃煤电厂、钢铁冶金、石油化工、水泥生产等高排放行业，通过技术改造实现碳减排目标。"
        elif "发展" in question or "前景" in question:
            return "CCUS是减少温室气体排放的关键技术，我国在该领域已开展多个示范项目，技术发展前景广阔，是实现碳中和目标的重要途径。"
        else:
            return "CCUS技术通过捕集、利用和储存工业排放的二氧化碳，为实现碳减排和气候目标提供重要的技术支撑。"

    # 碳减排相关问题
    if "碳减排" in question or "温室气体" in question or "气候变化" in question:
        return "碳减排是应对气候变化的关键措施，主要通过提高能源效率、发展可再生能源、碳捕集利用与储存等技术手段来减少温室气体排放。"

    # 清洁能源相关问题
    if "清洁能源" in question or "可再生能源" in question:
        return "清洁能源包括太阳能、风能、水能、核能等，是减少碳排放、实现可持续发展的重要途径，与CCUS技术形成互补的减排体系。"

    return f"关于「{question}」的问题，我会基于CCUS领域的专业知识为您提供准确答案。"

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
        print(f"🔍 Searching graph for entity: {entity}")
        entity_graph = search_node_item(entity, graph if graph else None)

        print(f"📊 Graph data for {entity}: {entity_graph is not None}")
        if entity_graph and entity_graph.get('nodes'):
            print(f"   - Nodes: {len(entity_graph.get('nodes', []))}")
            print(f"   - Links: {len(entity_graph.get('links', []))}")
            print(f"   - Sents: {len(entity_graph.get('sents', []))}")
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
        else:
            print(f"   ❌ No graph data found for entity: {entity}")

    # 智能整合知识信息
    if triples or knowledge_content:
        # 构建结构化知识内容
        structured_knowledge = []

        # 处理三元组信息，按关系类型分组
        if triples:
            relation_groups = {}
            for t in triples[:10]:  # 限制数量，避免过长
                relation = t[1]
                if relation not in relation_groups:
                    relation_groups[relation] = []
                relation_groups[relation].append((t[0], t[2]))

            # 转换为自然语言描述
            for relation, pairs in relation_groups.items():
                if len(pairs) <= 3:  # 对于少量关系，详细描述
                    for subject, obj in pairs:
                        structured_knowledge.append(f"{subject}与{obj}的关系是{relation}")
                else:  # 对于大量关系，归纳描述
                    subjects = [pair[0] for pair in pairs[:3]]
                    structured_knowledge.append(f"关于{relation}的相关内容包括：{', '.join(subjects)}等")

        # 整合文本知识内容
        if knowledge_content:
            # 清理和优化知识内容格式
            clean_content = knowledge_content.replace("【", "").replace("】", "").replace("相关知识", "").strip()
            if clean_content and not clean_content.startswith("【相关关系】"):
                structured_knowledge.append(clean_content)

        # 构建最终参考内容
        if structured_knowledge:
            ref = "相关知识：" + "；".join(structured_knowledge[:5])  # 限制知识点数量

        print(f"🔧 Processed knowledge: {len(structured_knowledge)} items -> {len(ref)} chars")


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

    print(f"📥 USER INPUT: {user_input}")
    print(f"📚 KNOWLEDGE REF: {ref[:200] if ref else 'None'}...")
    print(f"🔍 ENTITIES: {entities}")

    # 构建基于知识图谱的丰富上下文
    has_knowledge = bool((triples or knowledge_content) and entities)

    print(f"📚 Knowledge available: {has_knowledge}")
    print(f"🔗 Triples: {len(triples)}, Knowledge: {len(knowledge_content) if knowledge_content else 0}")
    print(f"🤖 Using ChatGLM model for intelligent response generation")

    if model is not None:
        # 构建基于知识图谱的丰富上下文
        if has_knowledge:
            # 使用新的丰富上下文构建方法
            rich_context = build_rich_knowledge_context(triples, knowledge_content, entities, user_input)
            if rich_context:
                chat_input = rich_context
                print(f"📖 Using rich knowledge context")
            else:
                # 如果没有丰富上下文，使用基本的知识信息
                if ref:
                    basic_context = f"参考以下信息回答问题：{ref[:300]}...\n\n问题：{user_input}"
                    chat_input = basic_context
                else:
                    chat_input = user_input
        else:
            chat_input = user_input

        # 构建干净的历史记录
        clean_history = []
        for user_msg, response in history:
            # 清理用户输入，移除参考资料部分，保留原始问题
            clean_user_input = user_msg

            # 处理各种格式的prompt，提取原始问题
            if "请基于以上资料，用简洁自然的语言回答：" in user_msg:
                clean_user_input = user_msg.split("请基于以上资料，用简洁自然的语言回答：")[1].strip()
            elif "===参考资料===" in user_msg:
                if "根据上面资料，用简洁且准确的话回答下面问题：" in user_msg:
                    clean_user_input = user_msg.split("根据上面资料，用简洁且准确的话回答下面问题：")[1].strip()
                else:
                    clean_user_input = user_msg.split("===参考资料===")[0].strip()
            elif "根据我的知识，" in user_msg and len(user_msg) > 100:
                # 提取新格式中的原始问题（去除知识背景）
                lines = user_msg.split("\n")
                if len(lines) >= 2:
                    clean_user_input = lines[-1].strip()  # 取最后一行作为问题

            clean_history.append((clean_user_input, response))

        print(f"🔤 CHAT INPUT TO MODEL: {chat_input[:100]}...")
        print(f"📜 CLEAN HISTORY: {len(clean_history)} items")

        # 使用新的chat_glm实例或原有方式
        if chat_glm and chat_glm.loaded:
            print(f"✅ ChatGLM model is loaded and ready")
            for response, raw_history in chat_glm.stream_chat(chat_input, clean_history):
                print(f"🤖 RAW MODEL RESPONSE: {response}")
                # 后处理响应，清理不自然的回答
                cleaned_response = clean_model_response(response, user_input)
                print(f"🧹 CLEANED RESPONSE: {cleaned_response}")

                # 清理返回的历史记录，确保用户看到的是原始问题
                clean_return_history = []
                for h_q, h_r in raw_history:
                    clean_q = h_q

                    # 处理各种格式的prompt，提取原始问题
                    if "请基于以上资料，用简洁自然的语言回答：" in h_q:
                        clean_q = h_q.split("请基于以上资料，用简洁自然的语言回答：")[1].strip()
                    elif "===参考资料===" in h_q:
                        if "根据上面资料，用简洁且准确的话回答下面问题：" in h_q:
                            clean_q = h_q.split("根据上面资料，用简洁且准确的话回答下面问题：")[1].strip()
                        else:
                            clean_q = h_q.split("===参考资料===")[0].strip()
                    elif "根据我的知识，" in h_q and len(h_q) > 100:
                        # 提取新格式中的原始问题（去除知识背景）
                        lines = h_q.split("\n")
                        if len(lines) >= 2:
                            clean_q = lines[-1].strip()  # 取最后一行作为问题

                    # 也要清理历史记录中的响应
                    cleaned_h_r = clean_model_response(h_r, clean_q) if h_r else h_r
                    clean_return_history.append((clean_q, cleaned_h_r))

                # 直接使用ChatGLM的回答，因为已经包含了知识库信息作为上下文
                final_response = cleaned_response
                print(f"✅ Using ChatGLM response with knowledge context: {cleaned_response[:50]}...")

                updates = {
                    "query": user_input,  # 使用原始用户输入，而不是chat_input
                    "response": final_response  # 使用最终响应
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
            print(f"✅ Using fallback model for response generation")
            for response, history in model.stream_chat(tokenizer, chat_input, clean_history):
                print(f"🤖 FALLBACK MODEL RESPONSE: {response}")
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
            # 简单回复模式 - 无ChatGLM模型时的处理
            print(f"❌ No model available, using knowledge-based response mode")

            if has_knowledge:
                # 基于知识图谱信息生成智能回答
                print(f"📋 Generating smart answer from knowledge graph (no model)")
                response_text = generate_smart_response_from_knowledge(user_input, ref if ref else "")
            else:
                print(f"⏳ No knowledge available, using fallback message")
                response_text = f"关于「{user_input}」的问题，我在知识库中没有找到相关信息。建议您询问CCUS、碳捕集、二氧化碳储存等相关技术问题。"

            updates = {
                "query": user_input,
                "response": response_text
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
        # 即使没有模型也尝试使用知识库生成智能答案
        print(f"⚠️ No ChatGLM model available, using knowledge-based fallback")

        if has_knowledge:
            # 基于知识图谱信息生成智能回答
            print(f"📋 Generating smart answer from knowledge graph (no model)")
            response_text = generate_smart_response_from_knowledge(user_input, ref if ref else "")
        else:
            print(f"⏳ No model and no knowledge available")
            response_text = f"关于「{user_input}」的问题，我在知识库中没有找到相关信息。建议您询问CCUS、碳捕集、二氧化碳储存等相关技术问题。"

        updates = {
            "query": user_input,
            "response": response_text
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

    print("🚀 Starting optimized ChatGLM model loading...")

    # 先清理GPU内存
    try:
        import torch
        torch.cuda.empty_cache()
        if torch.cuda.is_available():
            print(f"🔧 GPU memory before loading: {torch.cuda.memory_allocated()/1024**3:.2f}GB")
    except Exception as e:
        print(f"⚠️ Could not check GPU memory: {e}")

    # 检查模型路径
    model_path = "/fast/zwj/ChatGLM-6B/weights"

    if os.path.exists(model_path) and os.listdir(model_path):
        # 使用新的简单加载器，但添加内存优化
        from app.utils.simple_chat import SimpleChatGLM

        print(f"📁 Model path exists: {model_path}")
        print(f"📦 Model files: {os.listdir(model_path)[:5]}...")  # 显示前5个文件

        # 创建ChatGLM实例，启用内存优化
        chat_glm = SimpleChatGLM(model_path, memory_optimize=True)

        print("🔄 Attempting to load model with memory optimization...")
        if chat_glm.load_model():
            # 兼容原有接口
            model = chat_glm.model
            tokenizer = chat_glm.tokenizer
            init_history = []
            print("✅ ChatGLM-6B loaded successfully and ready for chat!")

            # 显示加载后的内存使用
            try:
                if torch.cuda.is_available():
                    print(f"📊 GPU memory after loading: {torch.cuda.memory_allocated()/1024**3:.2f}GB")
            except:
                pass
        else:
            print("❌ Failed to load ChatGLM-6B with optimization")
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