import uvicorn
from starlette.applications import Starlette
from a2a.server.apps.jsonrpc.starlette_app import A2AStarletteApplication
from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from currency_agent_executor import CurrencyAgentExecutor
from a2a.types import AgentSkill, AgentCard, AgentCapabilities

currency_skill = AgentSkill(
    id="currency-exchange",
    name="货币汇率查询",
    description="查询两种货币之间的实时汇率，支持常见币种代码和中文名。",
    tags=["currency", "exchange", "rate"],
    examples=["USD 转换为 JPY", "查询欧元对人民币汇率"],
    inputModes=["text/plain"],
    outputModes=["text/plain"],
)

agent_card = AgentCard(
    name="Currency Exchange Agent",
    description="专注于货币转换和汇率查询的智能 Agent，基于 Frankfurter API 实时获取汇率。",
    version="1.0.0",
    url="http://localhost:8000/",
    protocolVersion="0.2.5",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    skills=[currency_skill],
    capabilities=AgentCapabilities(streaming=True),
)

# 1. 实例化 AgentExecutor
agent_executor = CurrencyAgentExecutor()
# 2. 实例化 TaskStore
store = InMemoryTaskStore()
# 3. 实例化 DefaultRequestHandler
handler = DefaultRequestHandler(agent_executor, store)
# 4. 构建 A2AStarletteApplication
app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler).build()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 