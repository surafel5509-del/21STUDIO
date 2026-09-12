import asyncio
import json
from typing import Any, Awaitable, Callable

from app.agent.tools import TOOLS, execute_tool

ToolChat = Callable[[list[dict[str, Any]], list[dict[str, Any]]], Awaitable[Any]]


def _message_to_dict(message: Any) -> dict[str, Any]:
    if isinstance(message, dict):
        return message
    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)
    if hasattr(message, "dict"):
        return message.dict(exclude_none=True)
    return {
        key: getattr(message, key)
        for key in ("role", "content", "tool_calls")
        if hasattr(message, key) and getattr(message, key) is not None
    }


def _tool_calls(message: Any) -> list[Any]:
    calls = getattr(message, "tool_calls", None)
    if calls is not None:
        return calls
    if isinstance(message, dict):
        return message.get("tool_calls") or []
    return []


def _call_field(call: Any, field: str, default: Any = None) -> Any:
    if isinstance(call, dict):
        return call.get(field, default)
    return getattr(call, field, default)


def _function_field(call: Any, field: str, default: Any = None) -> Any:
    function = _call_field(call, "function", {})
    if isinstance(function, dict):
        return function.get(field, default)
    return getattr(function, field, default)


async def run_tool_loop(
    messages: list[dict[str, Any]],
    chat: ToolChat,
    max_rounds: int = 5,
) -> str:
    """Run model -> tool calls -> tool results until a final answer is returned."""
    for _ in range(max_rounds):
        response = await chat(messages, TOOLS)
        message = response.choices[0].message
        calls = _tool_calls(message)

        messages.append(_message_to_dict(message))
        if not calls:
            content = getattr(message, "content", None)
            if content is None and isinstance(message, dict):
                content = message.get("content")
            return content if isinstance(content, str) else str(content or "")

        for call in calls:
            name = _function_field(call, "name")
            arguments = _function_field(call, "arguments", "{}")
            call_id = _call_field(call, "id", "")
            try:
                result = await asyncio.to_thread(execute_tool, name, arguments)
            except Exception as exc:
                result = json.dumps({"error": str(exc)})

            messages.append(
                {
                    "role": "tool",
                    "name": name,
                    "content": result,
                    "tool_call_id": call_id,
                }
            )

    raise RuntimeError("Tool loop exceeded the maximum number of rounds")
