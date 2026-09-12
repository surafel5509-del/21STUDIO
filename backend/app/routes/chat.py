import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agent.agent import Agent
from app.schemas import ChatRequest, ChatResponse

router = APIRouter()
agent = Agent()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply, provider, conversation_id = await agent.run(
            request.message, request.provider, request.conversation_id, request.mode, request.thinking_mode
        )
        return ChatResponse(reply=reply, provider=provider, conversation_id=conversation_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    async def events():
        try:
            yield f"data: {json.dumps({'type': 'status', 'status': 'thinking', 'mode': request.mode})}\n\n"
            if request.mode == "research":
                yield f"data: {json.dumps({'type': 'status', 'status': 'researching', 'label': 'Searching sources and comparing findings'})}\n\n"
            async for chunk, provider, conversation_id in agent.stream(
                request.message, request.provider, request.conversation_id, request.mode, request.thinking_mode
            ):
                yield f"data: {json.dumps({'type': 'token', 'content': chunk, 'provider': provider, 'conversation_id': conversation_id})}\n\n"
            yield "data: {\"type\":\"done\"}\n\n"
        except RuntimeError as exc:
            yield f"data: {json.dumps({'type': 'error', 'error': str(exc)})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
