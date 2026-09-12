from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse
from app.providers.router import choose_provider
from app.agent.agent import Agent

router = APIRouter()
agent = Agent()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    provider = choose_provider(request.provider)
    reply = await agent.run(request.message)
    return ChatResponse(reply=reply, provider=provider)
