"""
对话上下文管理器
实现多轮筛选和实体跟踪功能
"""

import json
from collections import defaultdict
from app.utils.graph_utils import search_node_item, get_entity_details


class ContextManager:
    """对话上下文管理器"""

    def __init__(self):
        self.conversation_entities = []  # 对话中提到的实体
        self.entity_focus_history = []   # 实体关注历史
        self.topic_context = {}          # 话题上下文
        self.last_graph = None           # 上次搜索的图谱

    def update_context(self, user_input, entities, graph):
        """更新对话上下文"""
        print(f"🔄 Updating context with entities: {entities}")

        # 更新实体列表
        for entity in entities:
            if entity not in self.conversation_entities:
                self.conversation_entities.append(entity)
                self.entity_focus_history.append({
                    "entity": entity,
                    "query": user_input,
                    "mentioned_count": 1
                })
            else:
                # 增加提及次数
                for item in self.entity_focus_history:
                    if item["entity"] == entity:
                        item["mentioned_count"] += 1
                        break

        # 保持最近的图谱
        if graph:
            self.last_graph = graph

        # 分析话题上下文
        self._analyze_topic_context(user_input, entities)

        print(f"📊 Context: {len(self.conversation_entities)} entities tracked")

    def _analyze_topic_context(self, user_input, entities):
        """分析话题上下文"""
        # 识别问题类型
        question_type = self._identify_question_type(user_input)

        # 更新话题上下文
        if question_type:
            self.topic_context.update({
                "current_question_type": question_type,
                "current_entities": entities,
                "last_query": user_input
            })

    def _identify_question_type(self, user_input):
        """识别问题类型"""
        query = user_input.lower()

        if any(word in query for word in ["是什么", "什么是", "介绍", "定义"]):
            return "definition"
        elif any(word in query for word in ["有哪些", "包括", "种类", "类型"]):
            return "enumeration"
        elif any(word in query for word in ["如何", "怎么", "方法", "步骤"]):
            return "procedure"
        elif any(word in query for word in ["为什么", "原因", "作用", "目的"]):
            return "explanation"
        elif any(word in query for word in ["关系", "联系", "相关", "区别"]):
            return "relationship"
        elif any(word in query for word in ["更多", "详细", "具体", "进一步"]):
            return "elaboration"
        else:
            return "general"

    def get_focused_search(self, new_entities):
        """获取聚焦搜索结果"""
        if not self.conversation_entities and not new_entities:
            return None

        # 合并当前实体和历史实体
        all_entities = list(set(self.conversation_entities + new_entities))

        # 构建聚焦图谱
        focused_graph = None

        for entity in all_entities[:5]:  # 限制实体数量
            entity_graph = search_node_item(entity, focused_graph)
            if entity_graph:
                if not focused_graph:
                    focused_graph = entity_graph
                else:
                    # 合并图谱
                    focused_graph = self._merge_graphs(focused_graph, entity_graph)

        return focused_graph

    def _merge_graphs(self, graph1, graph2):
        """合并两个图谱"""
        if not graph1:
            return graph2
        if not graph2:
            return graph1

        merged = {
            "nodes": graph1["nodes"].copy(),
            "links": graph1["links"].copy(),
            "sents": graph1["sents"].copy()
        }

        # 合并节点
        existing_nodes = {node["name"]: node for node in merged["nodes"]}
        for node in graph2["nodes"]:
            if node["name"] not in existing_nodes:
                node["id"] = len(merged["nodes"])
                merged["nodes"].append(node)

        # 合并链接
        for link in graph2["links"]:
            if link not in merged["links"]:
                merged["links"].append(link)

        # 合并句子
        for sent in graph2["sents"]:
            if sent not in merged["sents"]:
                merged["sents"].append(sent)

        return merged

    def get_context_aware_response_prefix(self, entities):
        """获取上下文感知的回答前缀"""
        if not self.conversation_entities:
            return ""

        # 检查是否是延续性问题
        if self.topic_context.get("current_question_type") == "elaboration":
            if self.conversation_entities:
                last_entities = ", ".join(self.conversation_entities[-2:])
                return f"基于前面讨论的{last_entities}，"

        # 检查是否有重复提及的实体
        repeated_entities = []
        for item in self.entity_focus_history:
            if item["mentioned_count"] > 1:
                repeated_entities.append(item["entity"])

        if repeated_entities:
            return f"继续关于{repeated_entities[0]}的讨论，"

        return ""

    def get_conversation_summary(self):
        """获取对话摘要"""
        if not self.conversation_entities:
            return None

        # 统计实体提及频率
        entity_counts = defaultdict(int)
        for item in self.entity_focus_history:
            entity_counts[item["entity"]] = item["mentioned_count"]

        # 按频率排序
        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_entities": len(self.conversation_entities),
            "most_discussed": sorted_entities[:3],
            "current_topic": self.topic_context.get("current_question_type", "general"),
            "entities": self.conversation_entities
        }

    def suggest_related_questions(self, current_entities):
        """根据上下文建议相关问题"""
        if not current_entities:
            return []

        suggestions = []
        entity = current_entities[0] if current_entities else None

        if entity:
            # 根据实体类型和上下文建议问题
            if any(keyword in entity for keyword in ["灭火器", "消防"]):
                suggestions = [
                    f"{entity}的工作原理是什么？",
                    f"{entity}有哪些类型？",
                    f"如何正确使用{entity}？",
                    f"{entity}的维护保养方法？"
                ]
            elif any(keyword in entity for keyword in ["潜水", "潜艇"]):
                suggestions = [
                    f"{entity}装备包括哪些？",
                    f"{entity}的安全注意事项？",
                    f"{entity}技术发展历程？",
                    f"{entity}在军事中的应用？"
                ]
            else:
                suggestions = [
                    f"{entity}的详细介绍？",
                    f"{entity}的相关技术？",
                    f"{entity}的应用领域？"
                ]

        return suggestions[:3]  # 限制建议数量


# 全局上下文管理器实例
context_manager = ContextManager()