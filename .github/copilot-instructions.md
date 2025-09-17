# Copilot Instructions for KnowledgeGraph-based-on-Raw-text-A27

## 项目架构与主要组件
- **核心目标**：从原始文本自动构建知识图谱，支持多轮迭代、精炼与扩展。
- **主要目录**：
  - `modules/`：核心算法与数据处理，包括知识图谱构建、模型训练、数据预处理、few-shot、SPN4RE、UIE-finetune等子模块。
  - `data/`：原始与中间数据、实验结果、schema定义。
  - `chat-kg/`：前端 Vue3 + Vite 项目，提供知识图谱可视化与交互。
  - `server/`：后端服务接口（如有）。

## 关键开发流程
- **数据预处理**：
  - 使用 `modules/prepare/preprocess.py` 或 `modules/fewshot_model/preprocess.py` 清洗、分句。
  - 例：`process_text(input_file, max_line_length)`。
- **数据标注与转换**：
  - 推荐用 doccano 标注，转换脚本见 `modules/Uie-finetune/annotation/doccano/doccano.py`。
  - 例：
    ```shell
    python doccano.py --doccano_file ./data/doccano_ext.json --task_type "ext" --save_dir ./data --splits 0.8 0.1 0.1
    ```
- **模型训练与知识图谱构建**：
  - 入口为 `modules/knowledge_graph_builder.py` 和 `modules/model_trainer.py`。
  - SPN4RE 训练主脚本：`modules/SPN4RE/main.py`，参数通过命令行传递。
  - 训练流程自动切分数据、保存中间结果、生成预测与 refined KG。
- **Few-shot 流程**：
  - 参考 `modules/fewshot_model/run_fewshot.py`，先分句再调用 `uie_execute`。

## 重要约定与模式
- **数据格式**：训练/验证/测试集均为 JSON，每行一个样本，字段结构需与模型/脚本兼容。
- **路径与参数**：所有脚本参数均通过命令行传递，默认路径可在各脚本内查找。
- **多轮迭代**：知识图谱构建支持多轮 refine/extend，详见 `ModelTrainer` 和 `knowledge_graph_builder.py`。
- **前后端联动**：前端通过 `/api` 代理访问后端（见 `chat-kg/vite.config.js`）。

## 常见命令与调试
- 数据预处理：`python modules/prepare/preprocess.py`
- 标注转换：`python modules/Uie-finetune/annotation/doccano/doccano.py ...`
- 模型训练：`python modules/SPN4RE/main.py ...`
- Few-shot：`python modules/fewshot_model/run_fewshot.py`
- 前端启动：
  ```shell
  cd chat-kg && npm install && npm run dev
  ```

## 依赖与集成
- 依赖 Python 3.8+，部分模块需 PaddlePaddle、ONNX、zhconv、paddlenlp 等。
- 前端依赖 Node.js、Vite、Vue3。
- 训练/推理需 GPU 环境，CUDA 设备通过 `CUDA_VISIBLE_DEVICES` 控制。

## 参考文件
- `modules/knowledge_graph_builder.py`、`modules/model_trainer.py`、`modules/SPN4RE/main.py`
- `modules/prepare/preprocess.py`、`modules/Uie-finetune/annotation/doccano/doccano.py`
- `chat-kg/vite.config.js`

---
如遇不明确的流程或参数，优先查阅对应模块源码与 README，或向维护者提问。
