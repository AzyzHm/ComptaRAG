from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.chats import (
    MAX_HISTORY_MESSAGES,
    add_message,
    create_chat,
    delete_chat,
    get_chat,
    get_messages,
    list_chats,
    rename_chat,
    title_from_query,
    touch_chat,
)
from core.security import get_current_user
from core.stats import record_usage
from graph.workflow import app

router = APIRouter(prefix="/chats", tags=["Chats"])


class MessageRequest(BaseModel):
    query: str


class RenameRequest(BaseModel):
    title: str


def _owned_chat_or_404(chat_id: str, uid: str) -> dict:
    chat = get_chat(chat_id)
    if chat is None or chat["owner_uid"] != uid:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.post("/")
async def start_chat(current_user: dict = Depends(get_current_user)):
    """Creates a new, empty chat owned by the caller."""
    return create_chat(current_user["uid"])


@router.get("/")
async def list_my_chats(current_user: dict = Depends(get_current_user)):
    """Lists the caller's chats, most recently active first."""
    return list_chats(current_user["uid"])


@router.get("/{chat_id}")
async def get_chat_detail(chat_id: str, current_user: dict = Depends(get_current_user)):
    """Returns a chat and its full message history. Only the owner can read it."""
    chat = _owned_chat_or_404(chat_id, current_user["uid"])
    chat["messages"] = get_messages(chat_id)
    return chat


@router.patch("/{chat_id}")
async def rename_my_chat(
    chat_id: str, body: RenameRequest, current_user: dict = Depends(get_current_user)
):
    """Renames a chat. Only the owner can rename it."""
    _owned_chat_or_404(chat_id, current_user["uid"])
    rename_chat(chat_id, body.title)
    return {"id": chat_id, "title": body.title}


@router.delete("/{chat_id}", status_code=204)
async def delete_my_chat(chat_id: str, current_user: dict = Depends(get_current_user)):
    """Deletes a chat and all of its messages. Only the owner can delete it."""
    _owned_chat_or_404(chat_id, current_user["uid"])
    delete_chat(chat_id)


@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: str, body: MessageRequest, current_user: dict = Depends(get_current_user)
):
    """Sends a message in an existing chat.

    Runs the agent with the chat's last MAX_HISTORY_MESSAGES messages as
    conversational context, stores both the user's message and the
    assistant's reply, rolls the reply's token cost into the caller's usage
    total, and (on the very first exchange) titles the chat from the query.
    """
    chat = _owned_chat_or_404(chat_id, current_user["uid"])

    history = [
        {"role": message["role"], "content": message["content"]}
        for message in get_messages(chat_id, limit=MAX_HISTORY_MESSAGES)
    ]

    add_message(chat_id, role="user", content=body.query)

    try:
        result = app.invoke({"query": body.query, "history": history})  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    answer = result["answer"]
    category = result.get("category")
    token_usage = result.get("token_usage")

    add_message(
        chat_id, role="assistant", content=answer, category=category, token_usage=token_usage
    )

    is_first_exchange = chat.get("title") in (None, "New chat")
    touch_chat(chat_id, title=title_from_query(body.query) if is_first_exchange else None)

    if token_usage:
        record_usage(current_user["uid"], token_usage)

    return {"response": answer, "category": category, "chat_id": chat_id}