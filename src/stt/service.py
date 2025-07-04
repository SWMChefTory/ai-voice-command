import uuid
from fastapi import WebSocket
import websockets
from .models.stt_session import STTSession
from .vito.client import VitoStreamingClient
from .spring.client import SpringStreamClient

class STTService:
    def __init__(self):
        self.sessions = STTSession()
        self.vito = VitoStreamingClient()
        self.spring = SpringStreamClient()

    async def create_session(self, ws: WebSocket):
        session_id = f"stt_{uuid.uuid4().hex[:8]}"
        vito_ws = await self.vito.connect()
        self.sessions.create_session(session_id, ws, vito_ws)
        return session_id, vito_ws

    async def remove_session(self, session_id: str):
        spring_ws, vito_ws = self.sessions.get_session(session_id)
        await self.vito.close(vito_ws)
        await self.spring.close(spring_ws)
        self.sessions.remove_session(session_id)

    async def stream_audio_chunk(self, session_id: str, chunk: bytes):
        ws : websockets.ClientConnection = self.sessions.get_session(session_id)[1]
        await self.vito.send_chunk(ws, chunk)

    async def send_text(self, session_id: str, text: str):
        ws : WebSocket = self.sessions.get_session(session_id)[0]
        await self.spring.send_text(ws, text)
