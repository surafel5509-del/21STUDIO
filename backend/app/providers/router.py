import os

from app.config import CEREBRAS_API_KEY, DEFAULT_PROVIDER, GROQ_API_KEY, MISTRAL_API_KEY

PROVIDERS = ("mistral", "groq", "cerebras")


def available_providers() -> list[str]:
    return list(PROVIDERS)


def configured_providers() -> list[str]:
    keys = {
        "mistral": MISTRAL_API_KEY,
        "groq": GROQ_API_KEY,
        "cerebras": CEREBRAS_API_KEY,
    }
    return [name for name in PROVIDERS if keys[name]]


def provider_order(requested: str = "auto") -> list[str]:
    configured = configured_providers()
    if not configured:
        return []

    if requested in PROVIDERS:
        return [requested] + [p for p in configured if p != requested]

    preferred = DEFAULT_PROVIDER if DEFAULT_PROVIDER in PROVIDERS else "cerebras"
    ordered = [preferred] + [p for p in configured if p != preferred]

    custom = os.getenv("PROVIDER_ORDER", "")
    if custom:
        custom_order = [p.strip() for p in custom.split(",") if p.strip() in configured]
        ordered = custom_order + [p for p in ordered if p not in custom_order]

    return ordered


def choose_provider(requested: str = "auto") -> str:
    order = provider_order(requested)
    return order[0] if order else ""
