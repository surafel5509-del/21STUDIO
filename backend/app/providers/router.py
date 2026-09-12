from app.config import DEFAULT_PROVIDER


def available_providers() -> list[str]:
    return ["mistral", "groq", "cerebras"]


def choose_provider(requested: str = "auto") -> str:
    if requested in available_providers():
        return requested
    if DEFAULT_PROVIDER in available_providers():
        return DEFAULT_PROVIDER
    return "groq"
