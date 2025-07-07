> **本项目由 [Cursor AI](https://www.cursor.so/) 自动生成和重构。**

# Currency Agent

基于 Python 的货币转换与汇率查询智能 Agent，支持流式响应和 JSON 格式输出，使用 [Frankfurter API](https://www.frankfurter.app/) 获取实时汇率。

## 功能特性
- 货币汇率查询与货币转换
- 支持自然语言输入（中英文币种名或货币代码）
- 响应始终为 JSON 格式，包含状态与数据
- 流式响应，实时反馈处理进度
- 完善的错误处理机制

## 依赖环境
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) 0.7.2（项目依赖管理）
- a2a-sdk==0.2.10
- requests

## 安装与运行
1. 安装 uv 并创建虚拟环境：
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r pyproject.toml
   ```
2. 运行主程序：
   ```bash
   uv run python main.py
   ```
3. 运行Client：
   ```bash
   uv run python test_a2a_client.py
   ```

## 用法示例
```
欢迎使用货币转换和汇率查询 Agent！请输入您的问题（如：USD 转换为 JPY，或 美元对日元汇率）：
用户: 查询欧元对人民币汇率
Agent: {'status': 'tool_use', 'data': '正在查询 EUR 到 CNY 的汇率...'}
Agent: {'status': 'completed', 'data': {'amount': 1.0, 'base': 'EUR', 'date': '2025-07-04', 'rates': {'CNY': 8.4285}}}
```

## 系统架构说明
- **系统提示词**：限定 Agent 只处理货币相关问题，所有响应为 JSON 格式。
- **主要方法**：
  - `__init__`：初始化 API 配置、对话历史
  - `get_exchange_rate`：调用 Frankfurter API 获取汇率
  - `stream`：流式处理用户请求，支持中间状态反馈
  - `_parse_currencies`：解析用户输入中的货币对
- **响应格式**：
  - `completed`：任务完成
  - `input_required`：需要用户补充输入
  - `error`：发生错误
  - `tool_use`：正在调用工具

## 错误处理
- API 请求失败、JSON 解析错误、无效响应格式等均有详细错误提示
- 响应始终为 `{status: ..., data: ...}` 结构，便于集成与调试

## 扩展建议
- 可集成更多货币 API 或本地缓存
- 可对接更复杂的对话管理与上下文理解

---

本项目仅用于学习与演示，Frankfurter API 免费公开，适合测试与开发用途。 