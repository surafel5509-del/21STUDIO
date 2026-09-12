import asyncio
from typing import Any

from mistralai.client import Mistral

from app.agent.tools import TOOLS
from app.config import MISTRAL_API_KEY

MODEL = "mistral-large-latest"


def _complete(messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None):
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY is not configured")
    client = Mistral(api_key=MISTRAL_API_KEY)
    return client.chat.complete(
        model=MODEL,
        messages=messages,
        tools=tools or TOOLS,
        tool_choice="auto" if tools else "none",
        parallel_tool_calls=False,
    )


async def chat(messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None):
    return await asyncio.to_thread(_complete, messages, tools)
