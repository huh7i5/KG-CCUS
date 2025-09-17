
# 暂时禁用PaddleNLP依赖，使用基于关键词的实体识别
# from paddlenlp import Taskflow
import json
import os

class Ner:
    def __init__(self):
        print("Warning: Using keyword-based NER instead of deep learning model")
        # 加载知识图谱中的实体作为词典
        self.entity_dict = self._load_entities_from_kg()

    def _load_entities_from_kg(self):
        """从知识图谱中加载实体词典"""
        entities = set()

        # 从data.json中加载实体
        data_path = "data/data.json"
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for node in data.get('nodes', []):
                        entity_name = node.get('name', '').strip()
                        if entity_name and len(entity_name) > 1:  # 过滤过短的实体
                            entities.add(entity_name)
                print(f"✅ Loaded {len(entities)} entities from knowledge graph")
            except Exception as e:
                print(f"❌ Error loading entities from {data_path}: {e}")

        # 添加一些常见的消防和海军相关关键词
        common_entities = {
            '灭火器', '消防', '火灾', '消防车', '消防员', '消防栓', '烟雾报警器',
            '潜水', '潜艇', '军舰', '舰艇', '海军', '潜水员', '呼吸器', '潜水装具',
            '舰艇损管', '损害管制', '水下作业', '救生设备', '防火设施',
            '江南大学', '大学', '学校', '教育', '研究', '测深仪', '声呐', '雷达'
        }
        entities.update(common_entities)

        return entities

    def predict(self, text):
        # 返回空列表作为临时解决方案
        return []

    def get_entities(self, text, etypes=None):
        '''获取句子中指定类型的实体

        Args:
            text: 句子
            etypes: 实体类型列表
        Returns:
            entities: 实体列表
        '''
        entities = []

        # 基于关键词匹配提取实体
        for entity in self.entity_dict:
            if entity in text and entity not in entities:
                entities.append(entity)

        # 按长度排序，优先选择较长的实体（避免匹配子串）
        entities.sort(key=len, reverse=True)

        # 去重：如果一个实体是另一个实体的子串，则移除较短的
        filtered_entities = []
        for entity in entities:
            is_substring = False
            for existing in filtered_entities:
                if entity in existing and entity != existing:
                    is_substring = True
                    break
            if not is_substring:
                filtered_entities.append(entity)

        print(f"🔍 Extracted entities from '{text}': {filtered_entities}")
        return filtered_entities[:5]  # 限制返回最多5个实体