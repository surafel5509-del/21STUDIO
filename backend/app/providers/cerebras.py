import asyncio

from cerebras.cloud.sdk import Cerebras

from app.config import CEREBRAS_API_KEY

MODEL = "gpt-oss-120b"


def _complete(message: str) -> str:
    if not CEREBRAS_API_KEY:
        raise RuntimeError("CEREBRAS_API_KEY is not configured")
    client = Cerebras(api_key=CEREBRAS_API_KEY)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": message}],
    )
    return response.choices[0].message.content or ""


async def chat(message: str) -> str:
    return await asyncio.to_thread(_complete, message)
