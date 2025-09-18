import json


def search_node_item(user_input, lite_graph=None):
    import os
    # 确保正确的数据文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, '..', '..', 'data', 'data.json')

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Warning: data.json not found at {data_path}")
        return None

    if lite_graph is None:
        lite_graph = {
            'nodes': [],
            'links': [],
            'sents': []
        }

    # 利用thefuzz库来选取最相近的节点
    # node_names = [node['name'] for node in data['nodes']]
    # user_input = process.extractOne(user_input, node_names)[0]

    DEEP = 1

    # search node
    search_nodes = [user_input]
    for d in range(DEEP):
        for serch_node in search_nodes:
            for edge in data['links']:
                source = data['nodes'][int(edge['source'])]
                target = data['nodes'][int(edge['target'])]
                if source['name'] in serch_node or serch_node in source['name'] or target['name'] in serch_node or serch_node in target['name']:
                # if source['name'] == serch_node or target['name'] == serch_node:
                    sent = data['sents'][edge['sent']]
                    if sent not in lite_graph['sents']:
                        edge['sent'] = len(lite_graph['sents'])
                        lite_graph['sents'].append(sent)
                    else:
                        edge['sent'] = lite_graph['sents'].index(sent)

                    if source not in lite_graph['nodes']:
                        source['id'] = len(lite_graph['nodes'])
                        lite_graph['nodes'].append(source)
                    else:
                        source['id'] = lite_graph['nodes'].index(source)

                    if target not in lite_graph['nodes']:
                        target['id'] = len(lite_graph['nodes'])
                        lite_graph['nodes'].append(target)
                    else:
                        target['id'] = lite_graph['nodes'].index(target)

                    edge['source'] = source['id']
                    edge['target'] = target['id']
                    lite_graph['links'].append(edge)

        if len(lite_graph['nodes']) == 0:
            break

        search_nodes = [node['name'] for node in lite_graph['nodes']]

    return lite_graph


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