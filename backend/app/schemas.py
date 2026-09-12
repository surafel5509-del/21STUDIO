from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    provider: str = "auto"


class ChatResponse(BaseModel):
    reply: str
    provider: str
