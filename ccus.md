# CCUS领域决策大模型工具改造超级详细攻略

## 前言说明

**重要提醒**: 原项目已经内置了完整的数据清洗流程，你**无需手动清洗数据**！系统会自动处理：
- 特殊字符过滤
- 繁体转简体
- 句子分割和重组
- 实体有效性验证
- 三元组质量过滤

你只需要准备原始的CCUS文本数据，其他都交给程序自动处理。

---

## 第一部分：数据准备（无需清洗）

### 1.1 数据收集范围

**收集以下类型的CCUS相关文档内容**：

#### A. 技术文档类
- CCUS技术白皮书
- 各类捕集技术说明（燃烧前、燃烧后、富氧燃烧）
- 利用技术文档（化工利用、生物利用、矿化利用）
- 封存技术资料（地质封存、海洋封存）
- 技术设备说明书
- 工程案例研究报告
- 技术经济性分析报告

#### B. 政策法规类
- 国家碳达峰碳中和政策文件
- CCUS专项支持政策
- 地方政府CCUS实施细则
- 碳交易相关政策
- 财税支持政策
- 环保监管要求
- 行业标准和规范

#### C. 行业应用类
- 电力行业CCUS应用
- 钢铁行业CCUS应用
- 水泥行业CCUS应用
- 化工行业CCUS应用
- 石化行业CCUS应用
- 各行业减排效果评估

#### D. 地区特征类
- 各省市产业结构分析
- 地质条件调查报告
- 区域减排目标和计划
- 地方产业园区特征
- 基础设施现状
- 经济发展水平数据

#### E. 成本效益类
- 投资成本分析
- 运营成本评估
- 经济效益测算
- 社会效益评价
- 环境效益分析
- 风险评估报告

### 1.2 数据格式要求

**准备一个大的txt文件**：
- **文件路径**: `data/raw_data.txt`
- **编码**: UTF-8
- **大小建议**: 2-10MB（原项目600KB，CCUS内容需要更丰富）
- **语言**: 中文为主（系统会自动繁转简）

### 1.3 数据内容示例

```txt
碳捕集利用与封存技术是实现碳中和目标的关键技术路径。燃烧后捕集技术适用于现有燃煤电厂，技术成熟度较高，投资成本约为每千瓦1500-2500元。该技术对电厂的煤质要求不高，适合我国以煤为主的能源结构。

钢铁行业是碳排放重点行业，全国钢铁企业年排放CO2约15亿吨。大型钢铁企业如宝钢集团采用高炉煤气回收技术，年减排效果可达100万吨CO2当量。钢铁行业实施CCUS技术可获得国家专项资金支持，最高补贴可达项目总投资的30%。

华北地区具备良好的地质封存条件，地下盐水层分布广泛，封存容量超过300亿吨CO2。河北省提出到2030年建设10个CCUS示范项目，总投资规模达到500亿元。该地区钢铁、化工企业集中，为CCUS技术应用提供了丰富的排放源。

富氧燃烧技术相比燃烧后捕集技术，能耗更低，但初期投资成本较高。该技术适用于新建电厂，对于现有电厂改造难度较大。某示范电厂采用富氧燃烧技术，单位发电量碳捕集成本降低至200元每吨CO2。

地质封存技术要求储层深度在800米以上，孔隙度大于10%，渗透率大于50毫达西。我国东部地区沉积盆地发育，具备大规模地质封存的条件。中石油在山东胜利油田实施CCUS项目，累计封存CO2超过100万吨，同时提高原油采收率15%。
```

### 1.4 数据质量检查清单

**准备数据时确保包含以下关键信息**：
- [ ] 技术名称和技术特征描述
- [ ] 适用行业和应用条件
- [ ] 投资成本和运营成本数据
- [ ] 减排效果和技术指标
- [ ] 政策支持和资金补贴信息
- [ ] 地区特征和地质条件
- [ ] 成功案例和失败教训
- [ ] 技术供应商和设备信息
- [ ] 环境影响和安全风险
- [ ] 市场前景和经济效益

---

## 第二部分：Schema设计

### 2.1 创建CCUS专用Schema

**新建文件**: `data/schema/schema_ccus.py`

```python
schema = {
    "CCUS技术": [
        # 技术特征
        "技术类型", "技术成熟度", "适用规模", "适用温度", "适用压力",
        "捕集效率", "纯度要求", "能耗水平", "占地面积", "设备寿命",

        # 成本效益
        "投资成本", "运营成本", "维护成本", "单位成本", "回收期",
        "经济效益", "减排效果", "能效比", "成本效益比",

        # 适用条件
        "适用行业", "适用企业", "排放源类型", "排放浓度", "排放量要求",
        "地质条件", "基础设施", "技术要求", "人才要求",

        # 供应商和设备
        "技术供应商", "核心设备", "关键材料", "工艺流程", "控制系统",

        # 风险因素
        "技术风险", "环境风险", "安全风险", "经济风险", "政策风险",

        # 发展前景
        "市场前景", "技术发展", "成本趋势", "应用推广", "标准规范"
    ],

    "行业": [
        # 行业特征
        "排放特征", "排放量", "排放浓度", "排放源分布", "减排目标",
        "技术基础", "改造难度", "投资能力", "政策支持力度",

        # 应用条件
        "适用技术", "技术选择", "实施条件", "改造方案", "新建方案",
        "配套设施", "运营模式", "商业模式",

        # 效果评估
        "减排效果", "成本效益", "环境效益", "社会效益", "经济效益",
        "示范效果", "推广价值", "复制性",

        # 发展趋势
        "发展规划", "投资计划", "技术路线", "政策导向", "市场需求"
    ],

    "地区": [
        # 基本特征
        "地理位置", "行政级别", "经济水平", "产业结构", "能源结构",
        "排放总量", "减排目标", "减排压力", "发展阶段",

        # 地质条件
        "地质结构", "储层条件", "封存潜力", "地质风险", "监测条件",
        "地下水", "地震活动", "地质稳定性",

        # 基础设施
        "交通条件", "电力供应", "水资源", "土地资源", "工业园区",
        "管道网络", "储存设施", "运输条件",

        # 政策环境
        "政策支持", "资金支持", "税收优惠", "监管要求", "审批流程",
        "环保要求", "安全要求", "标准规范",

        # 人才资源
        "技术人才", "管理人才", "科研院所", "高等院校", "培训机构",
        "技术服务", "运维能力"
    ],

    "政策": [
        # 政策基本信息
        "政策类型", "发布机构", "实施时间", "有效期", "适用范围",
        "政策目标", "政策工具", "实施机制",

        # 支持措施
        "资金支持", "财政补贴", "税收优惠", "金融支持", "土地支持",
        "技术支持", "人才支持", "平台支持",

        # 监管要求
        "环保要求", "安全要求", "技术标准", "质量标准", "监测要求",
        "报告要求", "审批要求", "验收要求",

        # 激励机制
        "示范奖励", "技术奖励", "减排奖励", "创新奖励", "应用奖励",
        "碳交易", "碳积分", "绿色金融",

        # 实施效果
        "政策效果", "实施进展", "问题挑战", "改进建议", "发展趋势"
    ],

    "项目": [
        # 项目基本信息
        "项目类型", "建设规模", "投资规模", "建设周期", "运营周期",
        "技术路线", "工艺流程", "主要设备",

        # 实施主体
        "项目业主", "技术方", "工程方", "投资方", "运营方",
        "合作模式", "股权结构", "管理模式",

        # 技术方案
        "技术选择", "工艺设计", "设备配置", "控制方案", "安全方案",
        "环保方案", "监测方案", "运维方案",

        # 经济效益
        "投资估算", "运营成本", "收益分析", "盈利模式", "风险分析",
        "融资方案", "商业模式", "经济评价",

        # 实施效果
        "建设进展", "运营效果", "减排效果", "经济效果", "环境效果",
        "社会效果", "示范效果", "推广价值",

        # 问题挑战
        "技术挑战", "经济挑战", "政策挑战", "管理挑战", "环境挑战",
        "解决方案", "改进措施", "经验教训"
    ],

    "成本": [
        "构成要素", "计算方法", "影响因素", "控制措施", "优化方案",
        "比较基准", "敏感性分析", "趋势预测"
    ],

    "效益": [
        "效益类型", "计算方法", "评价指标", "影响因素", "提升措施",
        "比较分析", "综合评价", "发展趋势"
    ],

    "风险": [
        "风险类型", "风险等级", "发生概率", "影响程度", "风险来源",
        "防控措施", "应急预案", "管理制度"
    ],

    "标准": [
        "标准类型", "适用范围", "技术要求", "性能指标", "检测方法",
        "实施要求", "认证机构", "发展趋势"
    ]
}
```

### 2.2 Schema设计原则

**实体关系设计考虑**：
1. **决策导向**: 重点关注影响技术选择的关键因素
2. **多维评估**: 从技术、经济、政策、环境等多个维度
3. **层次化**: 从宏观政策到微观技术细节
4. **可操作**: 关系定义要便于实际决策应用
5. **可扩展**: 预留未来新技术和新政策的空间

---

## 第三部分：文件修改详细清单

### 3.1 必须修改的文件

#### 文件1: `data/schema/schema_ccus.py`
**操作**: 新建文件
**内容**: 复制上面的schema定义
**作用**: 定义CCUS领域的实体关系抽取规则

#### 文件2: `modules/prepare/process.py`
**位置**: 第2行
**原内容**: `from data.schema import schema_v4`
**修改为**: `from data.schema import schema_ccus`

**位置**: 第10行
**原内容**: `relation_ie = Taskflow("information_extraction", schema=schema_v4.schema, batch_size=2)`
**修改为**: `relation_ie = Taskflow("information_extraction", schema=schema_ccus.schema, batch_size=2)`

#### 文件3: `main.py`
**位置**: 第15行
**原内容**: `parser.add_argument("--project", type=str, default="project_v1")`
**修改为**: `parser.add_argument("--project", type=str, default="ccus_v1")`

### 3.2 可选修改的文件

#### 文件4: `modules/knowledge_graph_builder.py`
**如需使用专门的CCUS预训练模型**：
**位置**: 第29行
**原内容**: `self.model_name_or_path = "./pretrained/bert-base-chinese"`
**修改为**: `self.model_name_or_path = "./pretrained/ccus-bert"`（如果有专用模型）

#### 文件5: `modules/prepare/filter.py`
**如需使用专门的CCUS预训练模型**：
**位置**: 第14行
**原内容**: `tokenizer = AutoTokenizer.from_pretrained('./pretrained/bert-base-chinese')`
**修改为**: `tokenizer = AutoTokenizer.from_pretrained('./pretrained/ccus-bert')`

### 3.3 新增决策模块文件

#### 文件6: `modules/ccus_decision_engine.py`
**操作**: 新建文件
**内容**:
```python
import json
import numpy as np
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
        with open(self.kg_path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f.readlines()]

    def extract_technology_info(self) -> Dict:
        """从知识图谱中提取技术信息"""
        tech_info = {}

        for item in self.kg_data:
            for relation in item['relationMentions']:
                tech = relation['em1Text']
                attr = relation['label']
                value = relation['em2Text']

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

        # 这里实现评分算法
        # 可以根据具体需求设计权重和评分规则

        base_score = 0.6  # 基础分

        # 技术成熟度加分
        if "技术成熟度" in preferences:
            if preferences["技术成熟度"] == "商业化":
                base_score += 0.2

        # 投资预算匹配度
        if "投资预算" in preferences:
            # 根据预算范围调整分数
            base_score += 0.1

        # 政策支持度
        if "政策支持" in policy_context:
            base_score += 0.1

        return min(base_score, 1.0)

    def recommend_technologies(self,
                             region_info: Dict,
                             policy_context: Dict,
                             preferences: Dict) -> List[Dict]:
        """推荐CCUS技术方案"""

        tech_info = self.extract_technology_info()
        recommendations = []

        for tech_name, tech_attrs in tech_info.items():
            score = self.calculate_suitability_score(
                tech_name, region_info, policy_context, preferences
            )

            recommendations.append({
                "technology_name": tech_name,
                "suitability_score": score,
                "attributes": tech_attrs,
                "reasons": self.generate_reasons(tech_name, tech_attrs, score)
            })

        # 按适用性评分排序
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)

        return recommendations[:5]  # 返回前5个推荐

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
            reasons.append(f"适用于{','.join(attributes['适用行业'][:2])}等行业")

        if "政策支持" in attributes:
            reasons.append("有政策支持")

        return reasons
```

#### 文件7: `server/app/views/ccus_decision.py`
**操作**: 新建文件
**内容**:
```python
from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from modules.ccus_decision_engine import CCUSDecisionEngine

mod = Blueprint('ccus_decision', __name__, url_prefix='/api/ccus')

# 初始化决策引擎
decision_engine = None

def init_decision_engine():
    global decision_engine
    kg_path = "data/ccus_v1/knowledge_graph.json"  # 根据实际路径调整
    if os.path.exists(kg_path):
        decision_engine = CCUSDecisionEngine(kg_path)

@mod.route('/decision', methods=['POST'])
def get_ccus_recommendation():
    """CCUS技术推荐API"""

    if decision_engine is None:
        return jsonify({"error": "决策引擎未初始化，请先完成知识图谱构建"}), 500

    try:
        data = request.get_json()

        region_info = data.get('region_info', {})
        policy_context = data.get('policy_context', {})
        preferences = data.get('preferences', {})

        recommendations = decision_engine.recommend_technologies(
            region_info, policy_context, preferences
        )

        return jsonify({
            "status": "success",
            "recommendations": recommendations,
            "total_count": len(recommendations)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mod.route('/technologies', methods=['GET'])
def get_all_technologies():
    """获取所有CCUS技术列表"""

    if decision_engine is None:
        return jsonify({"error": "决策引擎未初始化"}), 500

    try:
        tech_info = decision_engine.extract_technology_info()

        return jsonify({
            "status": "success",
            "technologies": list(tech_info.keys()),
            "total_count": len(tech_info)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

#### 文件8: `server/app/__init__.py`
**位置**: 第11行之后添加
**添加内容**:
```python
from app.views import ccus_decision
apps.register_blueprint(ccus_decision.mod)

# 初始化CCUS决策引擎
ccus_decision.init_decision_engine()
```

---

## 第四部分：详细操作步骤

### 4.1 环境准备

#### 步骤1: 检查Python环境
```bash
python --version  # 确保是3.8+
pip list | grep paddle  # 检查PaddleNLP是否安装
pip list | grep transformers  # 检查transformers是否安装
```

#### 步骤2: 安装额外依赖（如果需要）
```bash
pip install zhconv  # 繁简转换
pip install flask-cors  # Web服务跨域支持
```

### 4.2 数据准备步骤

#### 步骤1: 准备CCUS文本数据
1. 收集CCUS相关文档（参考第一部分清单）
2. 将所有内容复制到一个文本文件中
3. 保存为UTF-8编码的`data/raw_data.txt`
4. 确保文件大小在2-10MB之间

#### 步骤2: 数据质量检查
```bash
# 检查文件编码
file -i data/raw_data.txt

# 查看文件大小
ls -lh data/raw_data.txt

# 查看前几行内容
head -20 data/raw_data.txt
```

### 4.3 代码修改步骤

#### 步骤1: 创建CCUS Schema
```bash
# 创建新的schema文件
cp data/schema/schema_v4.py data/schema/schema_ccus.py

# 编辑文件，替换为CCUS专用schema（参考第二部分）
vim data/schema/schema_ccus.py
```

#### 步骤2: 修改代码引用
```bash
# 修改process.py
sed -i 's/schema_v4/schema_ccus/g' modules/prepare/process.py

# 修改main.py默认项目名
sed -i 's/project_v1/ccus_v1/g' main.py
```

#### 步骤3: 创建决策模块
```bash
# 创建决策引擎文件
touch modules/ccus_decision_engine.py
# 复制第三部分的代码内容

# 创建API接口文件
touch server/app/views/ccus_decision.py
# 复制第三部分的代码内容

# 修改Flask应用配置
# 在server/app/__init__.py中添加相应代码
```

### 4.4 运行和测试步骤

#### 步骤1: 运行知识图谱构建
```bash
# 设置GPU（可选）
export CUDA_VISIBLE_DEVICES=0

# 开始构建基础知识图谱
python main.py --project="ccus_v1" --gpu="0"

# 如果中途出错，可以从checkpoint恢复
python main.py --project="ccus_v1" --resume="data/ccus_v1/history/xxxx.json"
```

#### 步骤2: 监控构建进程
```bash
# 查看UIE抽取进度
tail -f data/ccus_v1/base.json

# 查看迭代训练进度
tail -f data/ccus_v1/iteration_v0/running_log.log

# 查看当前知识图谱状态
ls -la data/ccus_v1/
```

#### 步骤3: 启动Web服务
```bash
cd server
python main.py
```

#### 步骤4: 测试API接口
```bash
# 测试决策API
curl -X POST http://localhost:8000/api/ccus/decision \
  -H "Content-Type: application/json" \
  -d '{
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
      "投资预算": "10亿元"
    }
  }'

# 测试技术列表API
curl http://localhost:8000/api/ccus/technologies
```

---

## 第五部分：预期输出和效果

### 5.1 知识图谱构建输出

#### 文件结构预期
```
data/ccus_v1/
├── base.json                    # UIE原始抽取结果
├── base_filtered.json           # 自动过滤后结果
├── base_refined.json           # 人工筛选后的基础图谱
├── iteration_v0/               # 第一次迭代
│   ├── train.json              # 训练数据
│   ├── valid.json              # 验证数据
│   ├── test.json               # 测试数据
│   ├── prediction.json         # SPN4RE预测结果
│   ├── alphabet.json           # 关系ID映射
│   └── knowledge_graph.json    # 最终知识图谱
├── iteration_v1/               # 第二次迭代
└── history/                    # 历史checkpoint
```

#### 三元组样例
```json
{
  "id": 0,
  "sentText": "燃烧后捕集技术适用于现有燃煤电厂，投资成本约为每千瓦1500-2500元。",
  "relationMentions": [
    {
      "em1Text": "燃烧后捕集技术",
      "em2Text": "现有燃煤电厂",
      "label": "适用行业"
    },
    {
      "em1Text": "燃烧后捕集技术",
      "em2Text": "每千瓦1500-2500元",
      "label": "投资成本"
    }
  ]
}
```

### 5.2 决策API输出示例

#### 推荐结果格式
```json
{
  "status": "success",
  "recommendations": [
    {
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
    },
    {
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
    }
  ],
  "total_count": 2
}
```

### 5.3 性能预期

#### 数据处理性能
- **UIE抽取**: 每10行打印一次进度，约需30分钟-2小时（取决于数据量）
- **SPN4RE训练**: 每次迭代约需1-3小时（GPU环境）
- **总体时间**: 首次完整构建需4-8小时

#### 知识图谱规模
- **基础三元组**: 预期10万-50万个关系三元组
- **迭代扩展**: 每次迭代增加5%-15%的新关系
- **最终规模**: 预期达到100万+关系三元组

#### 决策准确性
- **技术覆盖**: 涵盖主要CCUS技术路线
- **政策匹配**: 准确识别政策支持条件
- **地区适配**: 基于地质和产业特征推荐

---

## 第六部分：常见问题解决

### 6.1 数据准备问题

**Q: 文本数据包含很多表格和图片怎么办？**
A: 只提取文字内容，忽略表格和图片。对于重要的表格数据，可以转换为文字描述。

**Q: 英文内容需要翻译吗？**
A: 建议翻译为中文，因为UIE模型主要针对中文优化。

**Q: 数据中有很多专业术语和缩写？**
A: 在数据中补充术语的完整定义，例如"CCUS即碳捕集利用与封存技术"。

### 6.2 运行问题

**Q: UIE抽取阶段内存不足？**
A: 减小batch_size，在`modules/prepare/process.py`第10行修改为`batch_size=1`。

**Q: SPN4RE训练时GPU显存溢出？**
A: 在`modules/model_trainer.py`中减小训练参数，如减少max_span_length。

**Q: 训练过程中断如何恢复？**
A: 使用`--resume`参数：`python main.py --resume="data/ccus_v1/history/最新checkpoint.json"`

### 6.3 效果问题

**Q: 抽取的关系质量不高？**
A:
1. 检查schema定义是否合理
2. 增加更多高质量的训练文本
3. 在human_refine阶段仔细筛选

**Q: 决策推荐不准确？**
A:
1. 优化`ccus_decision_engine.py`中的评分算法
2. 调整各因素的权重
3. 增加更多决策规则

**Q: 迭代扩展效果不明显？**
A:
1. 检查SPN4RE模型训练效果
2. 增加训练数据的多样性
3. 调整迭代停止条件

### 6.4 部署问题

**Q: Web服务启动失败？**
A:
1. 检查端口8000是否被占用
2. 确保知识图谱文件路径正确
3. 检查Python模块导入路径

**Q: API响应速度慢？**
A:
1. 优化决策算法的计算复杂度
2. 对知识图谱建立索引
3. 增加缓存机制

---

## 第七部分：高级优化建议

### 7.1 Schema优化

**动态Schema调整**：
根据抽取效果，动态调整实体类型和关系定义：
```python
# 可以根据数据特点添加更细化的关系
"CCUS技术": [
    "CO2捕集效率", "CO2纯度", "能耗指标", "占地系数",
    "设备投资", "运行成本", "维护费用", "人工成本"
]
```

### 7.2 决策算法优化

**多目标决策模型**：
```python
def calculate_comprehensive_score(self, tech_attrs, weights):
    """多目标综合评分"""
    scores = {
        'technical': self.calc_technical_score(tech_attrs),
        'economic': self.calc_economic_score(tech_attrs),
        'policy': self.calc_policy_score(tech_attrs),
        'environmental': self.calc_environmental_score(tech_attrs)
    }

    return sum(scores[k] * weights[k] for k in scores)
```

### 7.3 数据扩展策略

**外部数据集成**：
- 集成国际CCUS数据库
- 接入实时政策更新
- 连接经济数据API
- 整合地质数据库

### 7.4 评估和验证

**建立评估体系**：
1. **准确性评估**: 专家人工评估推荐结果
2. **覆盖度评估**: 检查技术和政策覆盖范围
3. **时效性评估**: 验证数据和政策的时效性
4. **用户满意度**: 收集实际使用反馈

---

## 总结

通过以上超详细的攻略，你可以将原有的舰艇损管知识图谱项目成功改造为CCUS领域决策大模型工具。整个过程**无需手动清洗数据**，系统会自动处理所有数据预处理工作。

**核心步骤回顾**：
1. 准备CCUS原始文本数据 → `data/raw_data.txt`
2. 设计CCUS专用Schema → `data/schema/schema_ccus.py`
3. 修改3个核心文件的引用关系
4. 新增决策引擎和API接口
5. 运行完整的知识图谱构建流程
6. 部署Web服务并测试API

**关键成功因素**：
- 数据质量：丰富、准确的CCUS文本数据
- Schema设计：符合决策需求的实体关系定义
- 算法优化：合理的技术推荐评分机制
- 持续改进：根据使用效果不断优化

按照这份攻略操作，你将获得一个能够根据地区特征、政策环境和技术偏好，智能推荐最适用CCUS技术方案的决策支持系统！

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "\u5206\u6790\u6570\u636e\u6e05\u6d17\u9700\u6c42\u548c\u6d41\u7a0b", "status": "completed", "activeForm": "\u5206\u6790\u6570\u636e\u6e05\u6d17\u9700\u6c42\u548c\u6d41\u7a0b"}, {"content": "\u8bbe\u8ba1CCUS\u9886\u57df\u7684schema\u7ed3\u6784", "status": "completed", "activeForm": "\u8bbe\u8ba1CCUS\u9886\u57df\u7684schema\u7ed3\u6784"}, {"content": "\u5236\u5b9a\u8be6\u7ec6\u7684\u6587\u4ef6\u4fee\u6539\u8ba1\u5212", "status": "completed", "activeForm": "\u5236\u5b9a\u8be6\u7ec6\u7684\u6587\u4ef6\u4fee\u6539\u8ba1\u5212"}, {"content": "\u7f16\u5199\u5b8c\u6574\u7684\u64cd\u4f5c\u6b65\u9aa4\u6307\u5357", "status": "completed", "activeForm": "\u7f16\u5199\u5b8c\u6574\u7684\u64cd\u4f5c\u6b65\u9aa4\u6307\u5357"}, {"content": "\u521b\u5efaccus.md\u653b\u7565\u6587\u6863", "status": "completed", "activeForm": "\u521b\u5efaccus.md\u653b\u7565\u6587\u6863"}]