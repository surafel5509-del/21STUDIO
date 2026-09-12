from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    provider: str = "auto"
    conversation_id: str | None = None
    mode: str = "chat"
    thinking_mode: bool = False
    attachment_context: str | None = Field(default=None, max_length=120_000)


class ChatResponse(BaseModel):
    reply: str
    provider: str
    conversation_id: str
