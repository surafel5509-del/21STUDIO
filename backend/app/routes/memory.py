from fastapi import APIRouter, HTTPException

from app.memory import delete_conversation, get_conversation

router = APIRouter()


@router.get("/memory/{conversation_id}")
def read_memory(conversation_id: str) -> dict:
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/memory/{conversation_id}")
def clear_memory(conversation_id: str) -> dict[str, bool]:
    deleted = delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True}
