import json
import numpy as np
import os
from typing import Dict, List, Tuple

class CCUSDecisionEngine:
    """CCUS技术决策引擎"""

    def __init__(self, knowledge_graph_path: str):
        """初始化决策引擎

        Args:
            knowledge_graph_path: 知识图谱文件路径
        """
        self.kg_path = knowledge_graph_path
        self.kg_data = self.load_knowledge_graph()

    def load_knowledge_graph(self) -> List[Dict]:
        """加载知识图谱数据"""
        if not os.path.exists(self.kg_path):
            print(f"Warning: Knowledge graph file not found: {self.kg_path}")
            return []

        try:
            with open(self.kg_path, 'r', encoding='utf-8') as f:
                return [json.loads(line) for line in f.readlines()]
        except Exception as e:
            print(f"Error loading knowledge graph: {e}")
            return []

    def extract_technology_info(self) -> Dict:
        """从知识图谱中提取技术信息"""
        tech_info = {}

        for item in self.kg_data:
            if 'relationMentions' not in item:
                continue

            for relation in item['relationMentions']:
                tech = relation.get('em1Text', '')
                attr = relation.get('label', '')
                value = relation.get('em2Text', '')

                if not tech or not attr or not value:
                    continue

                if tech not in tech_info:
                    tech_info[tech] = {}

                if attr not in tech_info[tech]:
                    tech_info[tech][attr] = []

                tech_info[tech][attr].append(value)

        return tech_info

    def calculate_suitability_score(self,
                                  technology: str,
                                  region_info: Dict,
                                  policy_context: Dict,
                                  preferences: Dict) -> float:
        """计算技术适用性评分"""

        # 基础分
        base_score = 0.6

        # 技术成熟度加分
        if "技术成熟度" in preferences:
            maturity = preferences["技术成熟度"]
            if "商业化" in maturity or "成熟" in maturity:
                base_score += 0.2
            elif "示范" in maturity:
                base_score += 0.15
            elif "研发" in maturity:
                base_score += 0.05

        # 投资预算匹配度
        if "投资预算" in preferences:
            budget = preferences["投资预算"]
            # 简化的预算匹配逻辑
            if "亿" in budget:
                base_score += 0.1
            elif "万" in budget:
                base_score += 0.05

        # 政策支持度
        if "政策支持" in policy_context:
            base_score += 0.1

        # 地区适配度
        if "地质条件" in region_info:
            geo_condition = region_info["地质条件"]
            if "适合" in geo_condition or "良好" in geo_condition:
                base_score += 0.1

        # 行业匹配度
        if "主要产业" in region_info and "适用行业" in preferences:
            industries = region_info["主要产业"]
            target_industries = preferences["适用行业"]
            # 检查行业匹配度
            for industry in industries:
                if industry in str(target_industries):
                    base_score += 0.05
                    break

        return min(base_score, 1.0)

    def recommend_technologies(self,
                             region_info: Dict,
                             policy_context: Dict,
                             preferences: Dict) -> List[Dict]:
        """推荐CCUS技术方案"""

        tech_info = self.extract_technology_info()
        recommendations = []

        if not tech_info:
            return [{
                "technology_name": "暂无技术数据",
                "suitability_score": 0.0,
                "attributes": {},
                "reasons": ["知识图谱尚未构建完成，请先运行UIE抽取和SPN4RE训练"]
            }]

        for tech_name, tech_attrs in tech_info.items():
            # 过滤掉明显不是技术名称的实体
            if len(tech_name) > 50 or len(tech_name) < 2:
                continue

            score = self.calculate_suitability_score(
                tech_name, region_info, policy_context, preferences
            )

            recommendations.append({
                "technology_name": tech_name,
                "suitability_score": round(score, 2),
                "attributes": tech_attrs,
                "reasons": self.generate_reasons(tech_name, tech_attrs, score)
            })

        # 按适用性评分排序
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)

        # 返回前5个推荐，如果没有数据则返回示例
        if not recommendations:
            return self._get_demo_recommendations()

        return recommendations[:5]

    def generate_reasons(self, tech_name: str, attributes: Dict, score: float) -> List[str]:
        """生成推荐理由"""
        reasons = []

        if score > 0.8:
            reasons.append("高度适合当前条件")
        elif score > 0.6:
            reasons.append("较为适合当前条件")
        else:
            reasons.append("需要进一步评估")

        # 根据技术属性添加具体理由
        if "适用行业" in attributes:
            industries = attributes["适用行业"][:2]  # 取前两个
            if industries:
                reasons.append(f"适用于{','.join(industries)}等行业")

        if "政策支持" in attributes:
            reasons.append("有政策支持")

        if "技术成熟度" in attributes:
            maturity = attributes["技术成熟度"]
            if maturity and "商业化" in str(maturity[0]):
                reasons.append("技术成熟度高")

        if "投资成本" in attributes:
            reasons.append("投资成本相对合理")

        return reasons

    def _get_demo_recommendations(self) -> List[Dict]:
        """返回演示推荐结果（当知识图谱为空时）"""
        return [{
            "technology_name": "燃烧后捕集技术",
            "suitability_score": 0.85,
            "attributes": {
                "适用行业": ["燃煤电厂", "钢铁企业"],
                "投资成本": ["每千瓦1500-2500元"],
                "技术成熟度": ["商业化"],
                "减排效果": ["85-95%"]
            },
            "reasons": [
                "高度适合当前条件",
                "适用于钢铁,电力等行业",
                "有政策支持",
                "技术成熟度高"
            ]
        }, {
            "technology_name": "地质封存技术",
            "suitability_score": 0.78,
            "attributes": {
                "适用条件": ["地下800米以上", "合适地质构造"],
                "封存容量": ["大规模封存"],
                "安全性": ["长期稳定"]
            },
            "reasons": [
                "较为适合当前条件",
                "地质条件良好",
                "封存容量大"
            ]
        }]

    def get_technology_statistics(self) -> Dict:
        """获取技术统计信息"""
        tech_info = self.extract_technology_info()

        return {
            "total_technologies": len(tech_info),
            "total_relations": sum(len(attrs) for attrs in tech_info.values()),
            "knowledge_graph_size": len(self.kg_data)
        }