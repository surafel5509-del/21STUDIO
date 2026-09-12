import asyncio
from typing import Any

from cerebras.cloud.sdk import Cerebras

from app.agent.tools import TOOLS
from app.config import CEREBRAS_API_KEY

MODEL = "gpt-oss-120b"


def _complete(messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None):
    if not CEREBRAS_API_KEY:
        raise RuntimeError("CEREBRAS_API_KEY is not configured")
    client = Cerebras(api_key=CEREBRAS_API_KEY)
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools or TOOLS,
        tool_choice="auto" if tools else "none",
    )


async def chat(messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None):
    return await asyncio.to_thread(_complete, messages, tools)
