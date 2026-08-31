from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.security import get_current_user
from graph.workflow import app

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str


@router.post("/")
async def chat_with_agent(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """main chat route, requires an authenticated user of any role"""
    try:
        result = app.invoke({"query": request.query})  # type: ignore
        return {"response": result["answer"], "category": result.get("category")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
