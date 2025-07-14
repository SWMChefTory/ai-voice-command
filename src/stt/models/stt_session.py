from fastapi import WebSocket
from typing import Dict

import websockets

class STTSessionCache:
    def __init__(self):
        self.sessions : Dict[str, tuple[WebSocket, websockets.ClientConnection]] = {}

    def create_session(self, session_id: str, websocket: WebSocket, vito_ws: websockets.ClientConnection):
        self.sessions[session_id] = (websocket, vito_ws)

    def remove_session(self, session_id: str):
        del self.sessions[session_id]
    
    def get_session(self, session_id: str) -> tuple[WebSocket, websockets.ClientConnection]:
        return self.sessions[session_id]
