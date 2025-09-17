"""
知识图谱格式转换器
将SPN4RE格式的知识图谱转换为前端可视化格式
"""

import json
import os


class KnowledgeGraphConverter:
    """将SPN4RE格式转换为前端格式的转换器"""

    def __init__(self):
        self.node_map = {}  # 实体名称到节点ID的映射
        self.nodes = []     # 节点列表
        self.links = []     # 边列表
        self.sents = []     # 句子列表
        self.categories = [] # 类别列表

    def convert_spn_to_frontend(self, spn_data_path, output_path):
        """
        将SPN4RE格式转换为前端格式

        Args:
            spn_data_path: SPN4RE格式的知识图谱文件路径
            output_path: 输出的前端格式文件路径
        """
        print(f"🔄 Converting knowledge graph from {spn_data_path} to {output_path}")

        # 读取SPN4RE格式数据
        with open(spn_data_path, 'r', encoding='utf-8') as f:
            spn_lines = [json.loads(line) for line in f.readlines()]

        # 重置数据结构
        self.node_map = {}
        self.nodes = []
        self.links = []
        self.sents = []
        self.categories = []

        # 收集所有关系类型作为类别
        relation_types = set()

        # 第一遍遍历：收集所有实体和关系类型
        for line in spn_lines:
            sent_text = line.get('sentText', '')
            relations = line.get('relationMentions', [])

            for rel in relations:
                em1_text = rel.get('em1Text', '').strip()
                em2_text = rel.get('em2Text', '').strip()
                label = rel.get('label', '').strip()

                if em1_text and em2_text and label:
                    # 添加实体到节点映射
                    self._add_entity(em1_text)
                    self._add_entity(em2_text)

                    # 收集关系类型
                    relation_types.add(label)

        # 设置类别
        self.categories = [{"name": rel_type} for rel_type in sorted(relation_types)]

        # 第二遍遍历：构建链接和句子
        for line in spn_lines:
            sent_text = line.get('sentText', '')
            relations = line.get('relationMentions', [])

            # 添加句子（如果有关系的话）
            if relations:
                sent_id = len(self.sents)
                self.sents.append(sent_text)

                # 为每个关系创建链接
                for rel in relations:
                    em1_text = rel.get('em1Text', '').strip()
                    em2_text = rel.get('em2Text', '').strip()
                    label = rel.get('label', '').strip()

                    if em1_text and em2_text and label and em1_text in self.node_map and em2_text in self.node_map:
                        link = {
                            "source": self.node_map[em1_text],
                            "target": self.node_map[em2_text],
                            "name": label,
                            "sent": sent_id
                        }
                        self.links.append(link)

        # 构造输出数据
        output_data = {
            "nodes": self.nodes,
            "links": self.links,
            "sents": self.sents,
            "categories": self.categories
        }

        # 保存到文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Knowledge graph converted successfully!")
        print(f"   - Nodes: {len(self.nodes)}")
        print(f"   - Links: {len(self.links)}")
        print(f"   - Sentences: {len(self.sents)}")
        print(f"   - Categories: {len(self.categories)}")

        return output_data

    def _add_entity(self, entity_name):
        """添加实体到节点列表"""
        if entity_name not in self.node_map:
            node_id = len(self.nodes)
            self.node_map[entity_name] = node_id

            # 根据实体类型设置不同的类别
            category = self._get_entity_category(entity_name)

            node = {
                "id": node_id,
                "name": entity_name,
                "category": category,
                "symbolSize": 8,
                "label": {
                    "show": True
                }
            }
            self.nodes.append(node)

    def _get_entity_category(self, entity_name):
        """根据实体名称推断类别"""
        # 这里可以根据需要添加更复杂的分类逻辑
        if any(keyword in entity_name for keyword in ['大学', '学校', '学院']):
            return 0  # 教育机构
        elif any(keyword in entity_name for keyword in ['公司', '企业', '集团']):
            return 1  # 企业机构
        elif any(keyword in entity_name for keyword in ['舰艇', '军舰', '潜艇', '航母']):
            return 2  # 军事装备
        elif any(keyword in entity_name for keyword in ['消防', '灭火', '救援']):
            return 3  # 消防设备
        elif any(keyword in entity_name for keyword in ['潜水', '呼吸', '装具']):
            return 4  # 潜水设备
        else:
            return 5  # 其他


def convert_latest_kg_to_frontend():
    """将最新的知识图谱转换为前端格式"""
    converter = KnowledgeGraphConverter()

    # 查找最新的知识图谱文件
    base_path = "data/project_v1"

    # 优先使用迭代版本
    for version in ['iteration_v1', 'iteration_v0']:
        kg_path = os.path.join(base_path, version, 'knowledge_graph.json')
        if os.path.exists(kg_path):
            print(f"🔍 Found knowledge graph: {kg_path}")
            output_path = "data/data.json"
            return converter.convert_spn_to_frontend(kg_path, output_path)

    # 使用base版本
    for base_file in ['base_refined.json', 'base_filtered.json', 'base.json']:
        kg_path = os.path.join(base_path, base_file)
        if os.path.exists(kg_path):
            print(f"🔍 Found base knowledge graph: {kg_path}")
            output_path = "data/data.json"
            return converter.convert_spn_to_frontend(kg_path, output_path)

    print("❌ No knowledge graph found!")
    return None


if __name__ == "__main__":
    convert_latest_kg_to_frontend()