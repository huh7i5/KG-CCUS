#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCUS知识图谱可视化文件生成脚本
将UIE抽取的CCUS关系数据转换为前端可视化格式
"""

import json
import os
from collections import defaultdict

def load_ccus_data(file_path):
    """加载CCUS知识图谱数据"""
    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
    return data

def extract_entities_and_relations(ccus_data):
    """从CCUS数据中提取实体和关系"""
    entities = {}  # entity_name -> {id, category, frequency}
    relations = []  # {source, target, relation_type, sentence_id}
    entity_sentences = defaultdict(list)  # entity -> [sentence_ids]

    entity_id = 0

    # 定义实体类型到类别ID的映射
    entity_type_mapping = {
        "CCUS技术": 0,
        "行业": 1,
        "地区": 2,
        "政策": 3,
        "项目": 4,
        "成本": 5,
        "效益": 6,
        "风险": 7,
        "标准": 8,
        "其他": 9
    }

    for item in ccus_data:
        sent_id = item.get('id', 0)
        sent_text = item.get('sentText', '')
        relation_mentions = item.get('relationMentions', [])

        for relation_mention in relation_mentions:
            for entity_type, entities_list in relation_mention.items():
                if not isinstance(entities_list, list):
                    continue

                for entity_data in entities_list:
                    if not isinstance(entity_data, dict):
                        continue

                    # 提取主实体
                    entity_text = entity_data.get('text', '').strip()
                    if not entity_text or len(entity_text) < 2:
                        continue

                    # 添加主实体
                    if entity_text not in entities:
                        entities[entity_text] = {
                            'id': entity_id,
                            'name': entity_text,
                            'category': entity_type_mapping.get(entity_type, 9),
                            'frequency': 1,
                            'symbolSize': 10
                        }
                        entity_id += 1
                    else:
                        entities[entity_text]['frequency'] += 1

                    entity_sentences[entity_text].append(sent_id)

                    # 提取关系
                    relations_dict = entity_data.get('relations', {})
                    for rel_type, rel_entities in relations_dict.items():
                        if not isinstance(rel_entities, list):
                            continue

                        for rel_entity_data in rel_entities:
                            if not isinstance(rel_entity_data, dict):
                                continue

                            rel_entity_text = rel_entity_data.get('text', '').strip()
                            if not rel_entity_text or len(rel_entity_text) < 2:
                                continue

                            # 添加关系实体
                            if rel_entity_text not in entities:
                                entities[rel_entity_text] = {
                                    'id': entity_id,
                                    'name': rel_entity_text,
                                    'category': 9,  # 默认类别
                                    'frequency': 1,
                                    'symbolSize': 8
                                }
                                entity_id += 1
                            else:
                                entities[rel_entity_text]['frequency'] += 1

                            entity_sentences[rel_entity_text].append(sent_id)

                            # 添加关系
                            relations.append({
                                'source': entities[entity_text]['id'],
                                'target': entities[rel_entity_text]['id'],
                                'name': rel_type,
                                'sent': sent_id
                            })

    return entities, relations, entity_sentences

def create_visualization_data(entities, relations, entity_sentences, ccus_data):
    """创建可视化数据格式"""

    # 创建句子文本映射
    sentences = {}
    for item in ccus_data:
        sentences[item.get('id', 0)] = item.get('sentText', '')

    # 转换实体为节点格式
    nodes = []
    for entity_name, entity_info in entities.items():
        # 计算节点大小（基于频率）
        symbol_size = max(8, min(50, entity_info['frequency'] * 3))

        node = {
            'id': entity_info['id'],
            'name': entity_name,
            'category': entity_info['category'],
            'symbolSize': symbol_size,
            'label': {
                'show': symbol_size > 20
            },
            'lines': entity_sentences[entity_name][:10]  # 最多保留10个句子ID
        }
        nodes.append(node)

    # 创建类别
    categories = [
        {'name': 'CCUS技术'},
        {'name': '行业'},
        {'name': '地区'},
        {'name': '政策'},
        {'name': '项目'},
        {'name': '成本'},
        {'name': '效益'},
        {'name': '风险'},
        {'name': '标准'},
        {'name': '其他'}
    ]

    # 创建可视化数据结构
    visualization_data = {
        'nodes': nodes,
        'links': relations,
        'categories': categories,
        'sents': sentences
    }

    return visualization_data

def main():
    """主函数"""
    input_file = "data/ccus_v1/base.json"
    output_file = "data/ccus_data.json"

    print("🚀 开始生成CCUS知识图谱可视化文件...")

    # 加载CCUS数据
    ccus_data = load_ccus_data(input_file)
    if not ccus_data:
        print(f"❌ 无法加载CCUS数据: {input_file}")
        return

    print(f"📊 加载了 {len(ccus_data)} 条CCUS数据记录")

    # 提取实体和关系
    entities, relations, entity_sentences = extract_entities_and_relations(ccus_data)

    print(f"🔍 提取了 {len(entities)} 个实体")
    print(f"🔗 提取了 {len(relations)} 个关系")

    # 生成可视化数据
    visualization_data = create_visualization_data(entities, relations, entity_sentences, ccus_data)

    # 保存可视化数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(visualization_data, f, ensure_ascii=False, indent=2)

    print(f"✅ CCUS知识图谱可视化文件已生成: {output_file}")
    print(f"📈 统计信息:")
    print(f"   - 节点数量: {len(visualization_data['nodes'])}")
    print(f"   - 边数量: {len(visualization_data['links'])}")
    print(f"   - 类别数量: {len(visualization_data['categories'])}")
    print(f"   - 句子数量: {len(visualization_data['sents'])}")

    # 显示实体分布
    category_counts = defaultdict(int)
    for node in visualization_data['nodes']:
        category_counts[visualization_data['categories'][node['category']]['name']] += 1

    print(f"\n📊 实体分布:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {category}: {count} 个")

if __name__ == "__main__":
    main()