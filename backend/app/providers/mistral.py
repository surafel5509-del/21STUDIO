import asyncio
from typing import Any, AsyncIterator

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


def _stream(messages: list[dict[str, Any]]):
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY is not configured")
    client = Mistral(api_key=MISTRAL_API_KEY)
    return client.chat.stream(model=MODEL, messages=messages)


async def stream(messages: list[dict[str, Any]]) -> AsyncIterator[str]:
    stream_response = await asyncio.to_thread(_stream, messages)
    for event in stream_response:
        data = getattr(event, "data", None)
        choices = getattr(data, "choices", None) if data is not None else None
        if not choices:
            continue
        delta = getattr(choices[0], "delta", None)
        content = getattr(delta, "content", None) if delta is not None else None
        if content:
            yield content
