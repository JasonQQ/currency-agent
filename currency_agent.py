import requests
import json
from typing import List, Dict, Any, Optional
import re

# 系统提示词
SYSTEM_PROMPT = (
    "你是一个专门处理货币转换和汇率查询的智能 Agent。所有响应必须为 JSON 格式。"
    "如需获取汇率，请调用 get_exchange_rate 工具。"
    "响应格式：{status: completed|input_required|error|tool_use, data: ...}"
)

class CurrencyAgent:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.frankfurter.app"):
        self.api_key = api_key
        self.base_url = base_url
        self.history: List[Dict[str, Any]] = []
        self.system_prompt = SYSTEM_PROMPT

    def add_to_history(self, role: str, content: Any):
        self.history.append({"role": role, "content": content})

    def get_exchange_rate(self, from_currency: str, to_currency: str, date: Optional[str] = None) -> Dict[str, Any]:
        """
        获取汇率信息，返回 JSON 格式。
        """
        try:
            if date:
                url = f"{self.base_url}/{date}"  # 历史汇率
            else:
                url = f"{self.base_url}/latest"  # 最新汇率
            params = {"from": from_currency, "to": to_currency}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {"status": "completed", "data": data}
        except requests.RequestException as e:
            return {"status": "error", "data": f"API 请求失败: {str(e)}"}
        except json.JSONDecodeError:
            return {"status": "error", "data": "API 响应格式错误，无法解析 JSON。"}
        except Exception as e:
            return {"status": "error", "data": f"未知错误: {str(e)}"}

    def stream(self, user_query: str):
        self.add_to_history("user", user_query)
        # 直接在stream中处理解析和status
        if "汇率" in user_query or "转换" in user_query:
            codes = re.findall(r"[A-Z]{3}", user_query)
            if len(codes) >= 2:
                from_currency, to_currency = codes[0], codes[1]
                yield {"status": "tool_use", "data": f"正在查询 {from_currency} 到 {to_currency} 的汇率..."}
                result = self.get_exchange_rate(from_currency, to_currency)
                self.add_to_history("agent", result)
                yield result
                return
            cn_map = {"美元": "USD", "日元": "JPY", "欧元": "EUR", "人民币": "CNY", "英镑": "GBP"}
            found = [cn_map[k] for k in cn_map if k in user_query]
            if len(found) >= 2:
                from_currency, to_currency = found[0], found[1]
                yield {"status": "tool_use", "data": f"正在查询 {from_currency} 到 {to_currency} 的汇率..."}
                result = self.get_exchange_rate(from_currency, to_currency)
                self.add_to_history("agent", result)
                yield result
                return
            yield {"status": "input_required", "data": "请明确说明需要查询的货币对。"}
        else:
            yield {"status": "input_required", "data": "请明确说明需要查询的货币对。"} 