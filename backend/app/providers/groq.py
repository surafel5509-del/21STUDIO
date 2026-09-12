import asyncio
from typing import Any

from groq import Groq

from app.agent.tools import TOOLS
from app.config import GROQ_API_KEY

MODEL = "llama-3.3-70b-versatile"


def _complete(messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    client = Groq(api_key=GROQ_API_KEY)
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools or TOOLS,
        tool_choice="auto" if tools else "none",
    )


async def chat(messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None):
    return await asyncio.to_thread(_complete, messages, tools)
