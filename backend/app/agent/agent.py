import asyncio

from app.agent.tool_loop import run_tool_loop
from app.providers import cerebras, groq, mistral
from app.providers.router import provider_order

PROVIDER_CLIENTS = {
    "mistral": mistral.chat,
    "groq": groq.chat,
    "cerebras": cerebras.chat,
}


class Agent:
    """Provider-backed agent with local tool calling and automatic fallback."""

    async def run(self, message: str, requested_provider: str = "auto") -> tuple[str, str]:
        errors: list[str] = []
        order = provider_order(requested_provider)
        if not order:
            raise RuntimeError("No AI provider is configured. Add at least one API key to backend/.env")

        messages = [{"role": "user", "content": message}]

        for provider in order:
            try:
                reply = await asyncio.wait_for(
                    run_tool_loop(messages.copy(), PROVIDER_CLIENTS[provider]),
                    timeout=90,
                )
                return reply, provider
            except Exception as exc:
                errors.append(f"{provider}: {exc}")

        raise RuntimeError("All configured AI providers failed. " + " | ".join(errors))
