from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.websockets.audio_handler import websocket_translate

app = FastAPI(title="BabelFlow", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.websocket("/ws/translate")(websocket_translate)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "babelflow"}
