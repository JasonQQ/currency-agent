import aiohttp
import asyncio
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import TaskStatusUpdateEvent, TaskState, TaskStatus, Message, TextPart, Task, Artifact, Part, Role
import uuid
from datetime import datetime
from currency_agent import CurrencyAgent

class CurrencyAgentExecutor(AgentExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = CurrencyAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_input = context.get_user_input()
        task_id = context.task_id or str(uuid.uuid4())
        context_id = context.context_id or str(uuid.uuid4())
        # 1. 发送 working 状态
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            contextId=context_id,
            final=False,
            kind="status-update",
            metadata=None,
            status=TaskStatus(state=TaskState.working, message=None, timestamp=datetime.utcnow().isoformat()+"Z"),
            taskId=task_id,
        ))
        try:
            for event in self.agent.stream(user_input):
                if event["status"] == "input_required":
                    await event_queue.enqueue_event(TaskStatusUpdateEvent(
                        contextId=context_id,
                        final=True,
                        kind="status-update",
                        metadata=None,
                        status=TaskStatus(state=TaskState.input_required, message=None, timestamp=datetime.utcnow().isoformat()+"Z"),
                        taskId=task_id,
                    ))
                    return
                elif event["status"] == "tool_use":
                    # 可选：推送中间状态
                    await event_queue.enqueue_event(TaskStatusUpdateEvent(
                        contextId=context_id,
                        final=False,
                        kind="status-update",
                        metadata=None,
                        status=TaskStatus(state=TaskState.working, message=None, timestamp=datetime.utcnow().isoformat()+"Z"),
                        taskId=task_id,
                    ))
                elif event["status"] == "completed":
                    data = event["data"]
                    rate = None
                    from_currency = None
                    to_currency = None
                    if isinstance(data, dict) and "base" in data and "rates" in data and isinstance(data["rates"], dict) and data["rates"]:
                        from_currency = data["base"]
                        to_currency = list(data["rates"].keys())[0]
                        rate = data["rates"][to_currency]
                    msg = Message(
                        contextId=context_id,
                        extensions=None,
                        kind="message",
                        messageId=str(uuid.uuid4()),
                        metadata=None,
                        parts=[Part(root=TextPart(kind="text", text=f"1 {from_currency} = {rate} {to_currency}" if rate else str(data)))],
                        referenceTaskIds=None,
                        role=Role.agent,
                        taskId=task_id,
                    )
                    await event_queue.enqueue_event(TaskStatusUpdateEvent(
                        contextId=context_id,
                        final=True,
                        kind="status-update",
                        metadata=None,
                        status=TaskStatus(state=TaskState.completed, message=msg, timestamp=datetime.utcnow().isoformat()+"Z"),
                        taskId=task_id,
                    ))
                    return
                elif event["status"] == "error":
                    await event_queue.enqueue_event(TaskStatusUpdateEvent(
                        contextId=context_id,
                        final=True,
                        kind="status-update",
                        metadata=None,
                        status=TaskStatus(state=TaskState.failed, message=None, timestamp=datetime.utcnow().isoformat()+"Z"),
                        taskId=task_id,
                    ))
                    return
        except Exception as e:
            await event_queue.enqueue_event(TaskStatusUpdateEvent(
                contextId=context_id,
                final=True,
                kind="status-update",
                metadata=None,
                status=TaskStatus(state=TaskState.failed, message=None, timestamp=datetime.utcnow().isoformat()+"Z"),
                taskId=task_id,
            ))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # 简单实现：直接推送 canceled 状态
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            contextId=context.context_id or str(uuid.uuid4()),
            final=True,
            kind="status-update",
            metadata=None,
            status=TaskStatus(state=TaskState.canceled, message=None, timestamp=datetime.utcnow().isoformat()+"Z"),
            taskId=context.task_id or str(uuid.uuid4()),
        )) 