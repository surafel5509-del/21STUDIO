import asyncio
from typing import AsyncIterator

from app.agent.tool_loop import run_tool_loop
from app.memory import ensure_conversation, get_history, save_turn
from app.providers import cerebras, groq, mistral
from app.providers.router import provider_order

PROVIDER_CLIENTS = {"mistral": mistral.chat, "groq": groq.chat, "cerebras": cerebras.chat}
PROVIDER_STREAMS = {"mistral": mistral.stream, "groq": groq.stream, "cerebras": cerebras.stream}

SYSTEM_PROMPT = """You are 21STUDIO, a polished professional AI workspace.

Answer naturally and clearly. Never produce random punctuation, broken fragments, or decorative symbols between words. Do not expose hidden chain-of-thought or private reasoning. When reasoning is useful, give a concise 'Approach' summary instead.

Formatting rules:
- Start with a clear title when the answer is substantial.
- Use short paragraphs and descriptive headings.
- Use numbered steps for procedures and bullets for lists.
- Use bold sparingly for key terms only.
- Put ALL programming code in fenced Markdown code blocks with the correct language tag.
- Never mix prose and code inside the same code block.
- Keep code complete and copy-ready; do not replace sections with '...' unless the user explicitly asks for a snippet.
- For code generation, explain the result briefly, then provide the complete code in clean code blocks.
- If using web research, synthesize findings, distinguish facts from uncertainty, and include a concise Sources section with exact URLs returned by the search tool.
- Prefer clean Markdown over ASCII art and avoid excessive punctuation.
"""


def _system_message(mode: str, thinking_mode: bool) -> dict[str, str]:
    mode_instruction = {
        "chat": "Mode: Chat. Be concise, conversational, and useful.",
        "agent": "Mode: Agent. Plan the task, use available tools when useful, and deliver a concrete result.",
        "research": "Mode: Research. MUST use web_search for current, source-backed or research requests. Search multiple results when useful, compare them, synthesize them, and include exact source URLs.",
    }.get(mode, "Mode: Chat.")
    thinking_instruction = (
        "Thinking mode is enabled: verify carefully and take extra planning time, but NEVER reveal private chain-of-thought. Return only a concise reasoning summary and the final result."
        if thinking_mode else
        "Thinking mode is off: answer directly while still checking your work."
    )
    return {"role": "system", "content": f"{SYSTEM_PROMPT}\n{mode_instruction}\n{thinking_instruction}"}


def _build_user_message(message: str, attachment_context: str | None) -> str:
    if not attachment_context:
        return message
    return f"{message}\n\n[ATTACHED DOCUMENT CONTEXT]\n{attachment_context}\n[END ATTACHED DOCUMENT CONTEXT]"


class Agent:
    """Provider-backed agent with persistent memory, tools, fallback, and streaming."""

    async def run(self, message: str, requested_provider: str = "auto", conversation_id: str | None = None, mode: str = "chat", thinking_mode: bool = False, attachment_context: str | None = None) -> tuple[str, str, str]:
        errors: list[str] = []
        order = provider_order(requested_provider)
        if not order:
            raise RuntimeError("No AI provider is configured. Add at least one API key to backend/.env")
        conversation_id = ensure_conversation(conversation_id)
        history = get_history(conversation_id)
        user_message = _build_user_message(message, attachment_context)
        messages = [_system_message(mode, thinking_mode), *history, {"role": "user", "content": user_message}]
        for provider in order:
            try:
                reply = await asyncio.wait_for(run_tool_loop(messages.copy(), PROVIDER_CLIENTS[provider]), timeout=90)
                save_turn(conversation_id, message, reply)
                return reply, provider, conversation_id
            except Exception as exc:
                errors.append(f"{provider}: {exc}")
        raise RuntimeError("All configured AI providers failed. " + " | ".join(errors))

    async def stream(self, message: str, requested_provider: str = "auto", conversation_id: str | None = None, mode: str = "chat", thinking_mode: bool = False, attachment_context: str | None = None) -> AsyncIterator[tuple[str, str, str]]:
        errors: list[str] = []
        order = provider_order(requested_provider)
        if not order:
            raise RuntimeError("No AI provider is configured. Add at least one API key to backend/.env")
        conversation_id = ensure_conversation(conversation_id)
        history = get_history(conversation_id)
        user_message = _build_user_message(message, attachment_context)
        messages = [_system_message(mode, thinking_mode), *history, {"role": "user", "content": user_message}]

        if mode in {"research", "agent"}:
            for provider in order:
                try:
                    reply = await asyncio.wait_for(run_tool_loop(messages.copy(), PROVIDER_CLIENTS[provider]), timeout=90)
                    save_turn(conversation_id, message, reply)
                    yield reply, provider, conversation_id
                    return
                except Exception as exc:
                    errors.append(f"{provider}: {exc}")
            raise RuntimeError("All configured AI providers failed. " + " | ".join(errors))

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
