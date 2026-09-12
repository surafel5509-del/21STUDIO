import asyncio
from typing import AsyncIterator

from app.agent.tool_loop import run_tool_loop
from app.memory import ensure_conversation, get_history, save_turn
from app.providers import cerebras, groq, mistral
from app.providers.router import provider_order

PROVIDER_CLIENTS = {"mistral": mistral.chat, "groq": groq.chat, "cerebras": cerebras.chat}
PROVIDER_STREAMS = {"mistral": mistral.stream, "groq": groq.stream, "cerebras": cerebras.stream}

SYSTEM_PROMPT = """You are 21STUDIO, a polished professional AI workspace.

Answer naturally and clearly. Never produce random punctuation, broken fragments, or decorative symbols between words. Do not expose hidden chain-of-thought or private reasoning. When reasoning is useful, give a concise 'Approach' or 'Key reasoning' summary instead.

Formatting rules:
- Start with a clear title when the answer is substantial.
- Use short paragraphs and descriptive headings.
- Use numbered steps for procedures and bullets for lists.
- Use bold sparingly for key terms only.
- Put ALL programming code in fenced Markdown code blocks with the correct language tag.
- Never mix prose and code inside the same code block.
- Keep code complete and copy-ready; do not replace sections with '...' unless the user explicitly asks for a snippet.
- For code generation, explain what the code does briefly, then provide the complete code in one or more clean code blocks.
- If using web research, synthesize the findings, distinguish facts from uncertainty, and include a concise Sources section with the URLs returned by the search tool.
- Prefer clean Markdown over ASCII art and avoid excessive punctuation.
"""


def _system_message(mode: str, thinking_mode: bool) -> dict[str, str]:
    mode_instruction = {
        "chat": "Mode: Chat. Be concise, conversational, and useful.",
        "agent": "Mode: Agent. Break complex tasks into actionable steps, use available tools when useful, and finish with a concrete result.",
        "research": "Mode: Research. Search when current or source-backed information is useful. Compare sources, synthesize findings, and cite the sources in a Sources section.",
    }.get(mode, "Mode: Chat.")
    thinking_instruction = (
        "Thinking mode is enabled: take extra care with planning and verification, but NEVER reveal private chain-of-thought. Return only a concise summary of the reasoning and the final result."
        if thinking_mode else
        "Thinking mode is off: answer directly while still checking your work."
    )
    return {"role": "system", "content": f"{SYSTEM_PROMPT}\n{mode_instruction}\n{thinking_instruction}"}


class Agent:
    """Provider-backed agent with persistent memory, tools, fallback, and streaming."""

    async def run(self, message: str, requested_provider: str = "auto", conversation_id: str | None = None, mode: str = "chat", thinking_mode: bool = False) -> tuple[str, str, str]:
        errors: list[str] = []
        order = provider_order(requested_provider)
        if not order:
            raise RuntimeError("No AI provider is configured. Add at least one API key to backend/.env")
        conversation_id = ensure_conversation(conversation_id)
        history = get_history(conversation_id)
        messages = [_system_message(mode, thinking_mode), *history, {"role": "user", "content": message}]
        for provider in order:
            try:
                reply = await asyncio.wait_for(run_tool_loop(messages.copy(), PROVIDER_CLIENTS[provider]), timeout=90)
                save_turn(conversation_id, message, reply)
                return reply, provider, conversation_id
            except Exception as exc:
                errors.append(f"{provider}: {exc}")
        raise RuntimeError("All configured AI providers failed. " + " | ".join(errors))

    async def stream(self, message: str, requested_provider: str = "auto", conversation_id: str | None = None, mode: str = "chat", thinking_mode: bool = False) -> AsyncIterator[tuple[str, str, str]]:
        errors: list[str] = []
        order = provider_order(requested_provider)
        if not order:
            raise RuntimeError("No AI provider is configured. Add at least one API key to backend/.env")
        conversation_id = ensure_conversation(conversation_id)
        history = get_history(conversation_id)
        messages = [_system_message(mode, thinking_mode), *history, {"role": "user", "content": message}]
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
