import asyncio
import httpx
from a2a.client.client import A2AClient
from a2a.types import SendMessageRequest, SendStreamingMessageRequest, MessageSendParams, Message, Part, TextPart, Role
import uuid

async def single_run_test(a2a_client):
    print("\n=== Single Run Test ===")
    ctx_id = f"ctx-client-{uuid.uuid4()}"
    task_id = f"task-client-{uuid.uuid4()}"
    msg = Message(
        kind="message",
        messageId=f"test-client-{uuid.uuid4()}",
        role=Role.user,
        parts=[Part(root=TextPart(kind="text", text="查询欧元对人民币汇率"))],
        contextId=ctx_id,
        taskId=task_id
    )
    params = MessageSendParams(message=msg)
    req = SendMessageRequest(id=1, jsonrpc="2.0", method="message/send", params=params)
    resp = await a2a_client.send_message(req)
    print(resp)

async def streaming_test(a2a_client):
    print("\n=== Streaming Test ===")
    ctx_id = f"ctx-client-{uuid.uuid4()}"
    task_id = f"task-client-{uuid.uuid4()}"
    msg = Message(
        kind="message",
        messageId=f"test-client-{uuid.uuid4()}",
        role=Role.user,
        parts=[Part(root=TextPart(kind="text", text="USD 转换为 JPY"))],
        contextId=ctx_id,
        taskId=task_id
    )
    params = MessageSendParams(message=msg)
    req = SendStreamingMessageRequest(id=2, jsonrpc="2.0", method="message/stream", params=params)
    async for event in a2a_client.send_message_streaming(req):
        print(event)

async def input_required_multi_turn_test(a2a_client):
    print("\n=== Input Required Multi-turn Test ===")
    context_id = f"ctx-input-required-{uuid.uuid4()}"
    task_id = f"task-input-required-{uuid.uuid4()}"
    # 第一步：模糊提问
    msg1 = Message(
        kind="message",
        messageId=f"input-required-1-{uuid.uuid4()}",
        role=Role.user,
        parts=[Part(root=TextPart(kind="text", text="请帮我查一下汇率"))],
        contextId=context_id,
        taskId=task_id
    )
    params1 = MessageSendParams(message=msg1)
    req1 = SendMessageRequest(id=201, jsonrpc="2.0", method="message/send", params=params1)
    resp1 = await a2a_client.send_message(req1)
    print(f"[Step 1] User: 请帮我查一下汇率")
    print(f"[Step 1] Agent: {resp1}")
    # 检查是否 input_required
    try:
        # 兼容 TaskStatus 结构体和字符串
        state = None
        if hasattr(resp1.root.result, 'status'):
            status = resp1.root.result.status
            if hasattr(status, 'state'):
                state = status.state
            elif isinstance(status, dict):
                state = status.get('state')
        if isinstance(state, str):
            state_str = state
        elif state is not None and hasattr(state, 'value'):
            state_str = state.value
        else:
            state_str = str(state)
    except Exception:
        state_str = None
    if state_str == "input-required":
        # 第二步：补全币种
        msg2 = Message(
            kind="message",
            messageId=f"input-required-2-{uuid.uuid4()}",
            role=Role.user,
            parts=[Part(root=TextPart(kind="text", text="USD 转换为 CNY"))],
            contextId=context_id,
            taskId=task_id
        )
        params2 = MessageSendParams(message=msg2)
        req2 = SendMessageRequest(id=202, jsonrpc="2.0", method="message/send", params=params2)
        resp2 = await a2a_client.send_message(req2)
        print(f"[Step 2] User: USD 转换为 CNY")
        print(f"[Step 2] Agent: {resp2}")
    else:
        print(f"[Step 2] 未进入 input_required 状态，实际 state={state_str}，测试失败")

async def main():
    async with httpx.AsyncClient() as client:
        a2a_client = await A2AClient.get_client_from_agent_card_url(client, "http://127.0.0.1:8000")
        await single_run_test(a2a_client)
        await streaming_test(a2a_client)
        await input_required_multi_turn_test(a2a_client)

if __name__ == "__main__":
    asyncio.run(main()) 