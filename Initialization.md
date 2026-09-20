# 环境核查与初始化约定

本文说明核查方式；当前环境、缺失项和执行结果只在 PROGRESS.md 维护。

在仓库根目录核查：

- `git status --short --branch`：分支和工作区状态。
- `uv --version`：项目工具是否可用。
- `uv python find`：项目选择的 Python 路径，与系统 python 别名区分。
- `uv lock --check`：锁文件是否存在且与依赖声明一致，失败须记录原因。
- `uv sync --locked`：严格按锁文件建立环境。
- `uv run python scripts/check.py`：依次执行静态、类型、单元、集成和端到端验证。

安装、启动和验证使用 README.md 中已经验证过的命令。
