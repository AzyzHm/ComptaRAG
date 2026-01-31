from fastapi import FastAPI
from app.routes import chat
from app.config.models import warm_up_embedding_model

app = FastAPI(title="Accounting Agent API")

warm_up_embedding_model()
app.include_router(chat.router)

@app.get("/")
def home():
    """ Simple Backend Status route """
    return {"status": "online"}