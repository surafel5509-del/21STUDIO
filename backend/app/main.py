from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS
from app.memory import init_memory
from app.routes import chat, files, health, memory

app = FastAPI(title="21STUDIO AI Agent API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_memory()


app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
app.include_router(files.router, prefix="/api")
