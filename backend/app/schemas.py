from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    provider: str = "auto"
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    provider: str
    conversation_id: str
