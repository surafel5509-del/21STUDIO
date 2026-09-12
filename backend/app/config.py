import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")

# Free-tier friendly model defaults. These can be overridden only when needed.
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")

DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "auto")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
VERCEL_URL = os.getenv("VERCEL_URL", "")
MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", "")

ALLOWED_ORIGINS = [origin.strip() for origin in FRONTEND_URL.split(",") if origin.strip()]
if VERCEL_URL:
    ALLOWED_ORIGINS.extend([
        f"https://{VERCEL_URL}",
        f"https://www.{VERCEL_URL}",
    ])
ALLOWED_ORIGINS = list(dict.fromkeys(ALLOWED_ORIGINS))
