import json
import re


def clean_text_for_json(text):
    """清理文本以确保JSON序列化安全"""
    if not isinstance(text, str):
        return text

    # 移除或替换问题字符
    text = text.replace('\n', ' ')  # 换行符替换为空格
    text = text.replace('\r', ' ')  # 回车符替换为空格
    text = text.replace('\t', ' ')  # 制表符替换为空格
    text = text.replace('"', "'")   # 双引号替换为单引号

    # 移除控制字符
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # 压缩多个空格为单个空格
    text = re.sub(r'\s+', ' ', text)

    # 移除首尾空格
    text = text.strip()

    # 限制长度避免过长的实体名
    if len(text) > 200:
        text = text[:197] + "..."

    return text

def search_node_item(user_input, lite_graph=None):
    """CCUS领域知识图谱检索功能"""
    import os

    # 确保正确的数据文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, '..', '..', 'data', 'data.json')

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"📊 Loaded knowledge graph with {len(data.get('nodes', []))} nodes and {len(data.get('links', []))} edges")
    except FileNotFoundError:
        print(f"⚠️  CCUS knowledge graph not found at {data_path}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON format in {data_path}")
        return None

    if lite_graph is None:
        lite_graph = {
            'nodes': [],
            'links': [],
            'sents': []
        }

    # CCUS领域优化的搜索策略
    SEARCH_DEPTH = 2  # 增加搜索深度以获取更多相关信息

    # 初始搜索节点
    search_terms = [user_input]

    # 添加CCUS相关的同义词扩展
    ccus_synonyms = {
        'ccus': ['碳捕集利用与储存', '碳捕集', '碳储存', '碳利用'],
        'ccs': ['碳捕集与储存', '碳封存'],
        'ccu': ['碳捕集与利用', '碳转化'],
        '二氧化碳': ['co2', 'CO₂', '温室气体'],
        '捕集': ['捕获', '分离', '收集'],
        '储存': ['封存', '储藏', '地质储存'],
        '利用': ['转化', '应用', '资源化']
    }

    user_lower = user_input.lower()
    for key, synonyms in ccus_synonyms.items():
        if key in user_lower:
            search_terms.extend(synonyms)

    print(f"🔍 CCUS graph search for: {user_input}")
    print(f"📝 Extended search terms: {search_terms}")

    found_nodes = set()

    for depth in range(SEARCH_DEPTH):
        new_search_terms = []

        for search_term in search_terms:
            for edge in data.get('links', []):
                try:
                    source_idx = int(edge['source'])
                    target_idx = int(edge['target'])

                    if source_idx >= len(data['nodes']) or target_idx >= len(data['nodes']):
                        continue

                    source = data['nodes'][source_idx].copy()
                    target = data['nodes'][target_idx].copy()

                    # 改进的匹配策略
                    source_match = _is_ccus_match(search_term, source['name'])
                    target_match = _is_ccus_match(search_term, target['name'])

                    if source_match or target_match:
                        # 添加句子信息
                        sent_key = str(edge.get('sent', ''))
                        if sent_key in data.get('sents', {}):
                            sent = data['sents'][sent_key]
                            if sent not in lite_graph['sents']:
                                edge_copy = edge.copy()
                                edge_copy['sent'] = len(lite_graph['sents'])
                                lite_graph['sents'].append(sent)
                            else:
                                edge_copy = edge.copy()
                                edge_copy['sent'] = lite_graph['sents'].index(sent)
                        else:
                            edge_copy = edge.copy()
                            edge_copy['sent'] = -1

                        # 添加节点
                        source_id = _add_node_to_graph(source, lite_graph)
                        target_id = _add_node_to_graph(target, lite_graph)

                        # 添加边
                        edge_copy['source'] = source_id
                        edge_copy['target'] = target_id

                        # 避免重复边
                        edge_exists = any(
                            link['source'] == edge_copy['source'] and
                            link['target'] == edge_copy['target'] and
                            link.get('name', '') == edge_copy.get('name', '')
                            for link in lite_graph['links']
                        )

                        if not edge_exists:
                            lite_graph['links'].append(edge_copy)

                        # 收集相关节点用于下一轮搜索
                        found_nodes.add(source['name'])
                        found_nodes.add(target['name'])

                except (KeyError, IndexError, ValueError) as e:
                    continue

        if depth < SEARCH_DEPTH - 1:
            # 准备下一轮搜索的节点
            search_terms = list(found_nodes)[:10]  # 限制搜索节点数量

        if len(lite_graph['nodes']) == 0:
            break

    print(f"✅ CCUS graph search complete: {len(lite_graph['nodes'])} nodes, {len(lite_graph['links'])} edges")
    return lite_graph if len(lite_graph['nodes']) > 0 else None

def _is_ccus_match(search_term, node_name):
    """CCUS领域的智能匹配策略"""
    if not search_term or not node_name:
        return False

    search_lower = search_term.lower().strip()
    node_lower = node_name.lower().strip()

    # 1. 精确匹配
    if search_lower == node_lower:
        return True

    # 2. 包含匹配
    if search_lower in node_lower or node_lower in search_lower:
        return True

    # 3. CCUS特殊匹配规则
    ccus_mappings = {
        'ccus': ['碳捕集利用与储存', '碳捕集', '二氧化碳'],
        'co2': ['二氧化碳', '温室气体', '碳'],
        '捕集': ['capture', '分离', '收集'],
        '储存': ['storage', '封存', '储藏'],
        '利用': ['utilization', '转化', '应用']
    }

    for key, values in ccus_mappings.items():
        if key in search_lower:
            if any(v in node_lower for v in values):
                return True
        if any(v in search_lower for v in values):
            if key in node_lower:
                return True

    return False

def _add_node_to_graph(node, lite_graph):
    """添加节点到图谱中，避免重复"""
    for i, existing_node in enumerate(lite_graph['nodes']):
        if existing_node['name'] == node['name']:
            return i

    node_copy = node.copy()
    node_copy['id'] = len(lite_graph['nodes'])
    lite_graph['nodes'].append(node_copy)
    return node_copy['id']


def convert_graph_to_triples(graph, entity=None):
    """将图谱转换为三元组格式，并添加相关句子信息"""
    triples = []
    for link in graph['links']:
        source = graph['nodes'][link['source']]
        target = graph['nodes'][link['target']]

        if entity is not None:
            if entity in source['name'] or entity in target['name']:
                triple = (source['name'], link["name"], target['name'])
                triples.append(triple)
        else:
            triple = (source['name'], link["name"], target['name'])
            triples.append(triple)

    return triples

def extract_knowledge_content(graph, entity=None):
    """提取知识内容，包括三元组和相关句子"""
    if not graph or not graph.get('nodes'):
        return ""

    content_parts = []

    # 添加实体相关的三元组信息
    triples = convert_graph_to_triples(graph, entity)
    if triples:
        content_parts.append("【相关关系】")
        for i, (subj, pred, obj) in enumerate(triples[:10]):  # 限制数量
            content_parts.append(f"{i+1}. {subj} {pred} {obj}")

    # 添加相关句子
    if graph.get('sents'):
        content_parts.append("\n【相关描述】")
        for i, sent in enumerate(graph['sents'][:5]):  # 限制数量
            content_parts.append(f"{i+1}. {sent}")

    return "\n".join(content_parts)

def get_entity_details(entity_name, graph=None):
    """获取实体的详细信息"""
    if not graph:
        graph = search_node_item(entity_name)

    if not graph or not graph.get('nodes'):
        return None

    details = {
        "name": entity_name,
        "related_entities": [],
        "relationships": [],
        "sentences": graph.get('sents', []),
        "total_connections": 0
    }

    # 找到该实体的所有关系
    for link in graph.get('links', []):
        source = graph['nodes'][link['source']]
        target = graph['nodes'][link['target']]
        relation = link.get('name', '')

        if entity_name in source['name'] or source['name'] in entity_name:
            details['relationships'].append({
                "type": "outgoing",
                "relation": relation,
                "target": target['name']
            })
            if target['name'] not in details['related_entities']:
                details['related_entities'].append(target['name'])

        elif entity_name in target['name'] or target['name'] in entity_name:
            details['relationships'].append({
                "type": "incoming",
                "relation": relation,
                "source": source['name']
            })
            if source['name'] not in details['related_entities']:
                details['related_entities'].append(source['name'])

    details['total_connections'] = len(details['relationships'])
    return details