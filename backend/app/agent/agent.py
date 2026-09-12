import asyncio

from app.providers import cerebras, groq, mistral
from app.providers.router import provider_order

PROVIDER_CLIENTS = {
    "mistral": mistral.chat,
    "groq": groq.chat,
    "cerebras": cerebras.chat,
}


class Agent:
    """Provider-backed agent with automatic fallback."""

    async def run(self, message: str, requested_provider: str = "auto") -> tuple[str, str]:
        errors: list[str] = []
        order = provider_order(requested_provider)
        if not order:
            raise RuntimeError("No AI provider is configured. Add at least one API key to backend/.env")

        for provider in order:
            try:
                reply = await asyncio.wait_for(PROVIDER_CLIENTS[provider](message), timeout=60)
                return reply, provider
            except Exception as exc:
                errors.append(f"{provider}: {exc}")

        raise RuntimeError("All configured AI providers failed. " + " | ".join(errors))
