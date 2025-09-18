# 基于知识图谱和知识库的大模型对话系统详细分析

## 项目概述

本项目是一个基于知识图谱和知识库的大模型对话系统，专注于舰艇损管和潜水技术领域。项目整体包含5个核心部分：**数据预处理**、**图谱构建**、**图谱补全**、**对话模型**、**网页呈现**。

## 项目目录结构

```
KnowledgeGraph-based-on-Raw-text-A27-main/
├── main.py                    # 项目主入口文件
├── README.md                  # 项目说明文档
├── .gitignore                 # Git忽略文件配置
├── data/                      # 数据目录
│   ├── raw_data.txt          # 原始文本数据
│   ├── clean_data.txt        # 清洗后的数据
│   ├── project_v1/           # 项目数据输出目录
│   └── schema/               # 实体关系定义模式
│       ├── schema_v1.py
│       ├── schema_v2.py
│       ├── schema_v3.py
│       └── schema_v4.py      # 当前使用的schema定义
├── modules/                   # 核心模块目录
│   ├── knowledge_graph_builder.py  # 知识图谱构建器
│   ├── model_trainer.py            # 模型训练器
│   ├── prepare/                     # 数据预处理模块
│   │   ├── preprocess.py           # 文本预处理
│   │   ├── process.py              # UIE关系抽取
│   │   ├── filter.py               # 自动过滤
│   │   ├── utils.py                # 人工筛选工具
│   │   └── cprint.py               # 彩色打印工具
│   ├── SPN4RE/                     # SPN4RE模型目录
│   │   └── main.py                 # SPN4RE训练主程序
│   ├── Uie-finetune/              # UIE微调目录
│   └── fewshot_model/             # 少样本学习模型
├── server/                    # Web服务器目录
│   ├── main.py               # 服务器启动文件
│   ├── app/                  # Flask应用
│   │   ├── __init__.py       # Flask应用初始化
│   │   ├── views/            # 视图层
│   │   └── utils/            # 工具函数
│   │       ├── chat_glm.py   # ChatGLM模型接口
│   │       ├── graph_utils.py # 图谱工具
│   │       └── ner.py        # 命名实体识别
│   └── weights/              # 模型权重文件
├── chat-kg/                  # 前端交互界面
├── pretrained/               # 预训练模型存储
├── weights/                  # 训练好的模型权重
├── demo/                     # 演示图片和视频
└── test/                     # 测试文件
```

## 核心模块详细分析

### 1. 主程序 (main.py)

**文件位置**: `main.py:1-46`

**核心函数**:
- `arg_parser()`: 参数解析器，支持项目名称、GPU设置、checkpoint恢复等参数
- `main执行流程`:
  1. 创建`KnowledgeGraphBuilder`实例
  2. 可选择从checkpoint恢复训练
  3. 执行`get_base_kg_from_txt()`生成基础知识图谱
  4. 迭代执行`run_iteration()`进行图谱扩展，最大迭代10次
  5. 监控扩展比例，当扩展比例<1%时停止迭代

### 2. 知识图谱构建器 (modules/knowledge_graph_builder.py)

**文件位置**: `modules/knowledge_graph_builder.py:1-151`

**主要类**: `KnowledgeGraphBuilder`

**核心函数**:

#### `__init__(self, args)` - 初始化函数
- **功能**: 设置文件路径和参数
- **关键路径**:
  - `self.text_path`: 原始文本文件路径
  - `self.base_kg_path`: 基础三元组文件路径
  - `self.refined_kg_path`: 筛选后三元组文件路径
  - `self.filtered_kg_path`: 仅过滤无筛选的三元组文件路径

#### `get_base_kg_from_txt(self)` - 基础知识图谱生成
- **功能**: 从原始文本生成基础知识图谱
- **流程**:
  1. `process_text()`: 清洗文本，切分句子为指定长度(480字符)
  2. `uie_execute()`: 使用UIE模型进行关系抽取
  3. `auto_filter()`: 使用BERT tokenizer验证实体有效性
  4. `refine_knowledge_graph()`: 人工筛选(fast_mode=True时跳过)

#### `run_iteration(self)` - 迭代扩展
- **功能**: 执行一次知识图谱扩展迭代
- **流程**:
  1. 读取上一次迭代结果
  2. 创建`ModelTrainer`实例
  3. 执行训练和测试(`train_and_test()`)
  4. 关系对齐(`relation_align()`)
  5. 精化和扩展(`refine_and_extend()`)
  6. 保存结果并增加版本号

#### `extend_ratio(self)` - 扩展比例计算
- **功能**: 计算当前迭代相对于前一次的扩展比例
- **计算方法**: `扩展的三元组数量 / 之前三元组总数`

#### `save(self, save_path)` 和 `load(self, load_path)` - 状态保存和加载
- **功能**: 支持训练状态的保存和恢复

### 3. 模型训练器 (modules/model_trainer.py)

**文件位置**: `modules/model_trainer.py:1-218`

**主要类**: `ModelTrainer`

**核心函数**:

#### `__init__(self, data_path, output_dir, model_name_or_path, gpu)` - 初始化
- **功能**: 设置训练参数和文件路径
- **自动执行**: `split_data()`数据分割, `generate_running_cmd()`生成运行命令

#### `split_data(self)` - 数据分割
- **功能**: 按5:2:3比例分割训练/验证/测试集
- **输出**: train.json, valid.json, test.json

#### `generate_running_cmd(self)` - 生成SPN4RE训练命令
- **功能**: 构建SPN4RE模型的训练命令
- **关键参数**:
  - max_epoch: 10
  - max_span_length: 10
  - num_generated_triples: 15
  - na_rel_coef: 0.25

#### `train_and_test(self)` - 训练和测试
- **功能**: 执行SPN4RE模型的训练和预测
- **输出**: prediction.json预测结果文件

#### `relation_align(self)` - 关系对齐
- **功能**: 将预测结果与测试集对齐，转换为SPN格式
- **流程**:
  1. 读取测试集和预测结果
  2. 读取关系ID映射表(alphabet.json)
  3. 将预测的关系ID转换为关系标签
  4. 过滤重复和无效的三元组
  5. 使用`auto_filter()`进行二次过滤

#### `refine_and_extend(self)` - 精化和扩展
- **功能**: 人工筛选预测结果并与原数据合并
- **流程**:
  1. 调用`refine_knowledge_graph()`进行人工筛选
  2. 将筛选后的结果与原始数据合并
  3. 输出最终的知识图谱文件

### 4. 数据预处理模块 (modules/prepare/)

#### preprocess.py - 文本预处理
**核心函数**:
- `clean_to_sentence(file_path)`: 清洗文本，保留中文、英文、数字、标点，繁转简
- `add_sentences(sentences, max_line_length)`: 按最大长度(480字符)重组句子
- `process_text(input_file, max_line_length)`: 完整的文本预处理流程

#### process.py - UIE关系抽取
**核心函数**:
- `paddle_relation_ie(content)`: 使用PaddleNLP的UIE模型进行信息抽取
- `rel_json(content)`: 解析UIE输出，提取三元组关系
- `uie_execute(texts)`: 批量处理文本，生成结构化的关系数据

#### filter.py - 自动过滤
**核心函数**:
- `auto_filter(items, model_name_or_path)`: 使用BERT tokenizer验证实体有效性
  - 过滤空实体或过长实体(>15 tokens)
  - 验证实体是否存在于原句中
  - 记录实体在句子中的位置信息

#### utils.py - 人工筛选工具
**核心函数**:
- `check_input(prompt, keys)`: 交互式输入验证
- `refine_knowledge_graph(kg_path, refined_kg_path, fast_mode)`: 人工筛选知识图谱
  - fast_mode=True时直接通过所有数据
  - 交互式显示三元组供人工判断

### 5. 实体关系模式定义 (data/schema/schema_v4.py)

**文件位置**: `data/schema/schema_v4.py:1-512`

**功能**: 定义UIE模型的实体类型和关系类型

**主要实体类型**:
- **事故**: 工作人员、安全标准、装备工具、安全隐患、紧急预案等(68个关系)
- **原因**: 应对方法、调查方法、时间因素、技术因素、环境因素等(28个关系)
- **措施**: 规模、作用、效果、维修、生产、灭火、清洁等(43个关系)
- **设施**: 维修人员、消毒方法、配置、升级、性能指标等(125个关系)
- **工具**: 使用人员、维修时间、标准、操作指南等(66个关系)
- **职位**: 上级、下属、要求、所属部门、职责等(11个关系)
- **人名**: 工作经历、履历、著作、事迹等(7个关系)
- **时间**: 年份、开始、结束、工作、季节等(37个关系)
- **组织**: 任务、职责、规模、协作、发展等(27个关系)
- **数值**: 大小、比值、范围、型号、编号等(10个关系)
- **属性**: 优点、缺点、处理方法、影响等(20个关系)
- **疾病**: 症状、原因、治疗、预防、后果等(22个关系)
- **其他**: 舰艇抗沉、潜水医学、损管作业等专业术语(24个关系)

### 6. Web服务器模块 (server/)

#### main.py - 服务器启动
**功能**:
- 启动ChatGLM模型
- 配置Flask应用在8000端口运行

#### app/__init__.py - Flask应用配置
**功能**:
- 配置CORS跨域支持
- 注册chat和graph蓝图路由
- 错误处理机制

### 7. SPN4RE模型 (modules/SPN4RE/)

**功能**: Set Prediction Network for Relation Extraction
- 基于BERT的关系抽取模型
- 支持多关系预测
- 用于知识图谱的迭代扩展

## 程序整体执行流程

### 阶段一: 基础知识图谱构建

1. **文本预处理** (`main.py:32` → `knowledge_graph_builder.py:99-132`)
   - 读取原始文本文件 (`data/raw_data.txt`)
   - 文本清洗和句子分割 (`preprocess.py:31-34`)
   - 按480字符重组句子

2. **UIE关系抽取** (`process.py:34-53`)
   - 使用PaddleNLP UIE模型
   - 基于schema_v4定义的实体关系模式
   - 批量处理文本，提取三元组关系

3. **自动过滤** (`filter.py:4-74`)
   - 使用BERT tokenizer验证实体有效性
   - 过滤空实体和过长实体
   - 验证实体在原句中的存在性

4. **人工筛选** (`utils.py:16-79`)
   - 交互式三元组质量评估
   - fast_mode下自动通过所有数据
   - 生成基础知识图谱文件

### 阶段二: 迭代扩展 (最多10次迭代)

1. **数据准备** (`model_trainer.py:74-93`)
   - 读取上一轮知识图谱数据
   - 按5:2:3比例分割训练/验证/测试集

2. **SPN4RE模型训练** (`model_trainer.py:94-103`)
   - 基于BERT的关系抽取模型
   - 训练10个epoch
   - 生成预测结果文件

3. **关系对齐和扩展** (`model_trainer.py:104-195`)
   - 将预测结果与测试集对齐
   - 过滤与原数据重复的关系
   - 自动过滤无效预测

4. **人工精化** (`model_trainer.py:196-217`)
   - 人工筛选新预测的关系
   - 与原始数据合并
   - 生成新版本知识图谱

5. **收敛判断** (`knowledge_graph_builder.py:71-96`)
   - 计算扩展比例 = 新增关系数 / 原关系数
   - 扩展比例 < 1% 时停止迭代

### 阶段三: 对话服务部署

1. **模型加载** (`server/main.py:11-12`)
   - 启动ChatGLM-6B模型
   - 加载训练好的知识图谱

2. **Web服务** (`server/app/__init__.py`)
   - Flask服务器监听8000端口
   - 支持跨域请求
   - 提供chat和graph API接口

## 关键技术栈

- **文本预处理**: zhconv(繁简转换), re(正则表达式)
- **关系抽取**: PaddleNLP UIE模型, schema定义
- **深度学习**: SPN4RE(Set Prediction Network), BERT, transformers
- **Web框架**: Flask, CORS
- **对话模型**: ChatGLM-6B
- **前端**: 基于React的交互界面

## 数据流向图

```
原始文本(raw_data.txt)
    ↓ [文本清洗]
清洗后文本
    ↓ [UIE关系抽取]
原始三元组(base.json)
    ↓ [自动过滤]
过滤后三元组(base_filtered.json)
    ↓ [人工筛选]
基础知识图谱(base_refined.json)
    ↓ [迭代循环]
├── 数据分割(train/valid/test)
├── SPN4RE训练
├── 关系预测
├── 关系对齐
├── 人工精化
└── 扩展后知识图谱(iteration_vN/knowledge_graph.json)
    ↓ [Web服务]
对话系统API接口
```

## 模型性能和参数

- **UIE模型**: 基于PaddleNLP预训练模型，支持零样本关系抽取
- **SPN4RE训练参数**:
  - 最大epoch: 10
  - 最大span长度: 10
  - 生成三元组数: 15
  - 梯度裁剪: 2.5
  - NA关系系数: 0.25
- **数据分割比例**: 训练集50%，验证集20%，测试集30%
- **收敛条件**: 扩展比例 < 1%
- **最大迭代次数**: 10次

## 项目特色

1. **领域专用**: 专注于舰艇损管和潜水技术领域
2. **迭代扩展**: 通过SPN4RE模型不断扩展知识图谱
3. **质量控制**: 自动过滤+人工筛选双重质量保证
4. **模块化设计**: 清晰的模块划分，便于维护和扩展
5. **完整工作流**: 从原始文本到对话服务的端到端解决方案

## 潜在改进点

1. **自动化程度**: 人工筛选环节可进一步自动化
2. **模型选择**: 可尝试更先进的关系抽取模型
3. **扩展策略**: 可优化迭代扩展的停止条件
4. **性能优化**: 可加入GPU并行训练支持
5. **评估机制**: 可加入更完善的知识图谱质量评估

---

**生成时间**: 2025年9月18日
**分析版本**: KnowledgeGraph-based-on-Raw-text-A27
**分析范围**: 完整项目结构和核心功能模块