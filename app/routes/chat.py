from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graph.workflow import app

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    query: str

@router.post("/")
async def chat_with_agent(request: ChatRequest):
    """ main chat route """
    try:
        result = app.invoke({"query": request.query}) # type: ignore
        return {"response": result["answer"], "category": result.get("category")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))