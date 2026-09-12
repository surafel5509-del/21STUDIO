import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "auto")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", "")
