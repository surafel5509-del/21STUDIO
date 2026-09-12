import asyncio

from mistralai.client import Mistral

from app.config import MISTRAL_API_KEY

MODEL = "mistral-large-latest"


def _complete(message: str) -> str:
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY is not configured")
    client = Mistral(api_key=MISTRAL_API_KEY)
    response = client.chat.complete(
        model=MODEL,
        messages=[{"role": "user", "content": message}],
    )
    content = response.choices[0].message.content
    return content if isinstance(content, str) else str(content)


async def chat(message: str) -> str:
    return await asyncio.to_thread(_complete, message)
