import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

api_key = os.getenv("gemini_api_key")

genai.configure(api_key=api_key) # type: ignore

model = genai.GenerativeModel("gemini-2.5-flash") # type: ignore

class ChatRequest(BaseModel):
    message: str
    history: list = [] 

@app.post("/chat")
async def chat_with_gemini(request: ChatRequest):
    try:
        gemini_history = []
        for msg in request.history:
            gemini_history.append({
                "role": msg["role"],
                "parts": msg["parts"]
            })

        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(request.message)
        
        formatted_history = []
        for content in chat_session.history:
            part_text = content.parts[0].text if content.parts else ""
            formatted_history.append({
                "role": content.role,
                "parts": [part_text]
            })

        return {
            "response": response.text,
            "updated_history": formatted_history
        }
        
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))