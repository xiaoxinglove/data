# Evaluation 模块

## 当前实现

backend/evaluation/evaluator.py 提供 Evaluator.run(result)，固定返回：

- faithfulness: None
- retrieval_quality: None

没有数据集、计算逻辑、阈值或回归入口；None 不代表指标通过。

## 目标边界

评估模块接收可追踪的检索与生成结果，根据明确数据集和指标产出可复验报告。
引入 LLM-as-Judge 前需定义模型、提示、抽样和稳定性限制。
