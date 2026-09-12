from fastapi import APIRouter, HTTPException

from app.agent.agent import Agent
from app.schemas import ChatRequest, ChatResponse

router = APIRouter()
agent = Agent()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply, provider, conversation_id = await agent.run(
            request.message,
            request.provider,
            request.conversation_id,
        )
        return ChatResponse(
            reply=reply,
            provider=provider,
            conversation_id=conversation_id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
