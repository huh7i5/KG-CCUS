from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from modules.ccus_decision_engine import CCUSDecisionEngine

mod = Blueprint('ccus_decision', __name__, url_prefix='/api/ccus')

# 初始化决策引擎
decision_engine = None

def init_decision_engine():
    """初始化CCUS决策引擎"""
    global decision_engine

    # 尝试多个可能的知识图谱路径
    possible_paths = [
        "data/ccus_v1/knowledge_graph.json",
        "data/ccus_v1/iteration_v0/knowledge_graph.json",
        "data/ccus_v1/base_refined.json",
        "data/ccus_v1/base_filtered.json",
        "data/ccus_v1/base.json"
    ]

    kg_path = None
    for path in possible_paths:
        if os.path.exists(path):
            kg_path = path
            break

    if kg_path:
        decision_engine = CCUSDecisionEngine(kg_path)
        print(f"CCUS决策引擎初始化成功，使用知识图谱: {kg_path}")
    else:
        # 即使没有知识图谱文件也初始化引擎，它会返回示例数据
        decision_engine = CCUSDecisionEngine("data/ccus_v1/knowledge_graph.json")
        print("CCUS决策引擎初始化（使用示例数据）")

@mod.route('/decision', methods=['POST'])
def get_ccus_recommendation():
    """CCUS技术推荐API

    请求格式:
    {
        "region_info": {
            "地区名称": "山东省",
            "主要产业": ["钢铁", "化工"],
            "地质条件": "适合封存"
        },
        "policy_context": {
            "政策支持": "CCUS示范项目",
            "资金支持": "国家专项资金"
        },
        "preferences": {
            "技术成熟度": "商业化",
            "投资预算": "10亿元",
            "适用行业": ["钢铁", "电力"]
        }
    }
    """

    if decision_engine is None:
        return jsonify({
            "error": "决策引擎未初始化，请先完成知识图谱构建",
            "status": "error"
        }), 500

    try:
        data = request.get_json() or {}

        region_info = data.get('region_info', {})
        policy_context = data.get('policy_context', {})
        preferences = data.get('preferences', {})

        recommendations = decision_engine.recommend_technologies(
            region_info, policy_context, preferences
        )

        return jsonify({
            "status": "success",
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "region_info": region_info,
            "policy_context": policy_context,
            "preferences": preferences
        })

    except Exception as e:
        return jsonify({
            "error": f"推荐过程中发生错误: {str(e)}",
            "status": "error"
        }), 500

@mod.route('/technologies', methods=['GET'])
def get_all_technologies():
    """获取所有CCUS技术列表API"""

    if decision_engine is None:
        return jsonify({
            "error": "决策引擎未初始化",
            "status": "error"
        }), 500

    try:
        tech_info = decision_engine.extract_technology_info()
        technologies = list(tech_info.keys())

        return jsonify({
            "status": "success",
            "technologies": technologies,
            "total_count": len(technologies),
            "sample_technologies": technologies[:10]  # 返回前10个作为样例
        })

    except Exception as e:
        return jsonify({
            "error": f"获取技术列表时发生错误: {str(e)}",
            "status": "error"
        }), 500

@mod.route('/statistics', methods=['GET'])
def get_statistics():
    """获取知识图谱统计信息API"""

    if decision_engine is None:
        return jsonify({
            "error": "决策引擎未初始化",
            "status": "error"
        }), 500

    try:
        stats = decision_engine.get_technology_statistics()

        return jsonify({
            "status": "success",
            "statistics": stats
        })

    except Exception as e:
        return jsonify({
            "error": f"获取统计信息时发生错误: {str(e)}",
            "status": "error"
        }), 500

@mod.route('/health', methods=['GET'])
def health_check():
    """健康检查API"""

    status = "healthy" if decision_engine is not None else "unhealthy"

    return jsonify({
        "status": status,
        "service": "CCUS Decision Engine",
        "version": "1.0.0"
    })

# 在模块加载时自动初始化
init_decision_engine()