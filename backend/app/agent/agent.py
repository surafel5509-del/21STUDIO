import asyncio
from typing import AsyncIterator

from app.agent.tool_loop import run_tool_loop
from app.memory import ensure_conversation, get_history, save_turn
from app.providers import cerebras, groq, mistral
from app.providers.router import provider_order

PROVIDER_CLIENTS = {
    "mistral": mistral.chat,
    "groq": groq.chat,
    "cerebras": cerebras.chat,
}

PROVIDER_STREAMS = {
    "mistral": mistral.stream,
    "groq": groq.stream,
    "cerebras": cerebras.stream,
}


class Agent:
    """Provider-backed agent with persistent memory, tools, fallback, and streaming."""

    async def run(
        self,
        message: str,
        requested_provider: str = "auto",
        conversation_id: str | None = None,
    ) -> tuple[str, str, str]:
        errors: list[str] = []
        order = provider_order(requested_provider)
        if not order:
            raise RuntimeError("No AI provider is configured. Add at least one API key to backend/.env")

        conversation_id = ensure_conversation(conversation_id)
        history = get_history(conversation_id)
        messages = history + [{"role": "user", "content": message}]

        for provider in order:
            try:
                reply = await asyncio.wait_for(
                    run_tool_loop(messages.copy(), PROVIDER_CLIENTS[provider]),
                    timeout=90,
                )
                save_turn(conversation_id, message, reply)
                return reply, provider, conversation_id
            except Exception as exc:
                errors.append(f"{provider}: {exc}")

        raise RuntimeError("All configured AI providers failed. " + " | ".join(errors))

    async def stream(
        self,
        message: str,
        requested_provider: str = "auto",
        conversation_id: str | None = None,
    ) -> AsyncIterator[tuple[str, str, str]]:
        errors: list[str] = []
        order = provider_order(requested_provider)
        if not order:
            raise RuntimeError("No AI provider is configured. Add at least one API key to backend/.env")

        conversation_id = ensure_conversation(conversation_id)
        history = get_history(conversation_id)
        messages = history + [{"role": "user", "content": message}]

        for provider in order:
            try:
                chunks: list[str] = []
                async for chunk in PROVIDER_STREAMS[provider](messages):
                    chunks.append(chunk)
                    yield chunk, provider, conversation_id
                reply = "".join(chunks)
                if reply:
                    save_turn(conversation_id, message, reply)
                return
            except Exception as exc:
                errors.append(f"{provider}: {exc}")

        raise RuntimeError("All configured AI providers failed. " + " | ".join(errors))
