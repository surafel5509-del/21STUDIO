import asyncio

from groq import Groq

from app.config import GROQ_API_KEY

MODEL = "llama-3.3-70b-versatile"


def _complete(message: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": message}],
    )
    return response.choices[0].message.content or ""


async def chat(message: str) -> str:
    return await asyncio.to_thread(_complete, message)
