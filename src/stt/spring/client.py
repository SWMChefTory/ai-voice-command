from fastapi import WebSocket

class SpringStreamClient:
    async def send_text(self, ws: WebSocket, text: str):
        await ws.send_text(text)

    async def close(self, ws: WebSocket):
        await ws.close()