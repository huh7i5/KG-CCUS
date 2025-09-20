
import json
import os
import re

class Ner:
    """CCUS领域命名实体识别模块"""

    def __init__(self):
        print("🔧 Initializing CCUS Domain NER System...")
        # 加载CCUS领域实体词典
        self.entity_dict = self._load_ccus_entities()
        self.patterns = self._build_patterns()

    def _load_ccus_entities(self):
        """加载CCUS领域实体词典"""
        entities = set()

        # 从知识图谱中加载实体
        data_path = "data/data.json"
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for node in data.get('nodes', []):
                        entity_name = node.get('name', '').strip()
                        if entity_name and len(entity_name) > 1:
                            entities.add(entity_name)
                print(f"✅ Loaded {len(entities)} entities from knowledge graph")
            except Exception as e:
                print(f"❌ Error loading entities from {data_path}: {e}")

        # CCUS领域核心实体
        ccus_entities = {
            # 技术类型
            'CCUS', 'CCS', 'CCU', '碳捕集', '碳利用', '碳储存', '碳封存',
            '后燃烧捕集', '预燃烧捕集', '富氧燃烧', '直接空气捕集', 'DAC',
            '膜分离', '化学吸收', '物理吸附', '吸收法', '吸附法',

            # 化学物质和材料
            '二氧化碳', 'CO2', 'MEA', 'MDEA', '胺类溶剂', '离子液体',
            '金属有机框架', 'MOF', '分子筛', '活性炭', '氧化钙',

            # 设备和工艺
            '吸收塔', '再生塔', '压缩机', '热交换器', '反应器', '分离器',
            '管道运输', '船舶运输', 'IGCC', '整体煤气化联合循环',

            # 应用行业
            '燃煤电厂', '火力发电', '钢铁冶金', '水泥生产', '石油化工',
            '煤化工', '天然气发电', '生物质发电', '工业锅炉',

            # 地理和项目
            '鄂尔多斯', '大庆油田', '胜利油田', '华北油田', '渤海湾',
            '深部咸水层', '枯竭油气藏', '煤层气储层', '盐穴储存',

            # 政策和标准
            '碳中和', '碳达峰', '双碳目标', '碳排放权', '碳交易',
            '碳配额', '碳足迹', '温室气体', '气候变化', '巴黎协定',

            # 技术指标
            '捕集率', '储存容量', '泄漏率', '能耗', '成本效益',
            '生命周期评估', 'LCA', '技术成熟度', '经济性分析'
        }
        entities.update(ccus_entities)

        return entities

    def _build_patterns(self):
        """构建实体识别模式"""
        patterns = []

        # 数值+单位模式
        patterns.extend([
            r'\d+(?:\.\d+)?(?:万吨|吨|千吨|Mt|Gt|立方米|m³)',
            r'\d+(?:\.\d+)?%',
            r'\d+(?:\.\d+)?(?:度|℃|°C|MPa|bar|kPa)',
            r'\d+(?:\.\d+)?(?:年|月|日|小时|h|天)',
        ])

        # 技术名称模式
        patterns.extend([
            r'[A-Z]{2,6}技术',
            r'.{1,4}捕集技术',
            r'.{1,4}储存技术',
            r'.{1,4}利用技术',
        ])

        return [re.compile(pattern) for pattern in patterns]

    def predict(self, text):
        """预测接口（兼容性保留）"""
        return self.get_entities(text)

    def get_entities(self, text, etypes=None):
        """获取句子中的CCUS领域实体

        Args:
            text: 输入文本
            etypes: 实体类型列表（保留兼容性，但在CCUS领域不使用）
        Returns:
            entities: 提取到的实体列表
        """
        entities = []
        text_processed = text.strip()

        # 1. 基于词典的精确匹配
        dict_entities = self._extract_dict_entities(text_processed)
        entities.extend(dict_entities)

        # 2. 基于模式的匹配
        pattern_entities = self._extract_pattern_entities(text_processed)
        entities.extend(pattern_entities)

        # 3. 去重和过滤
        filtered_entities = self._filter_entities(entities)

        print(f"🔍 CCUS NER result for '{text}': {filtered_entities}")
        return filtered_entities[:8]  # 返回最多8个实体

    def _extract_dict_entities(self, text):
        """基于词典提取实体"""
        entities = []
        text_lower = text.lower()

        # 按长度倒序排序，优先匹配长实体
        sorted_entities = sorted(self.entity_dict, key=len, reverse=True)

        for entity in sorted_entities:
            entity_lower = entity.lower()
            if entity_lower in text_lower:
                # 检查边界，避免部分匹配
                import re
                pattern = re.compile(r'\b' + re.escape(entity_lower) + r'\b', re.IGNORECASE)
                if pattern.search(text) or entity_lower in text_lower:
                    entities.append(entity)
                    # 从文本中移除已匹配的实体，避免重复匹配
                    text_lower = text_lower.replace(entity_lower, ' ', 1)

        return entities

    def _extract_pattern_entities(self, text):
        """基于模式提取实体"""
        entities = []

        for pattern in self.patterns:
            matches = pattern.findall(text)
            for match in matches:
                if match and len(match.strip()) > 1:
                    entities.append(match.strip())

        return entities

    def _filter_entities(self, entities):
        """过滤和去重实体"""
        if not entities:
            return []

        # 去除重复项
        unique_entities = list(dict.fromkeys(entities))

        # 移除被包含的短实体
        filtered = []
        for entity in unique_entities:
            is_contained = False
            for other in unique_entities:
                if (entity != other and
                    len(entity) < len(other) and
                    entity.lower() in other.lower()):
                    is_contained = True
                    break

            if not is_contained:
                filtered.append(entity)

        # 按相关性排序（CCUS核心术语优先）
        ccus_core_terms = {'ccus', 'ccs', 'ccu', '碳捕集', '碳储存', '碳利用', '二氧化碳'}

        def entity_priority(entity):
            entity_lower = entity.lower()
            if any(core in entity_lower for core in ccus_core_terms):
                return 0  # 最高优先级
            elif any(keyword in entity_lower for keyword in ['碳', '捕集', '储存', '利用', 'co2']):
                return 1  # 高优先级
            else:
                return 2  # 普通优先级

        filtered.sort(key=lambda x: (entity_priority(x), -len(x)))
        return filtered