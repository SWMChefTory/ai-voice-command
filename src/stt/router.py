import asyncio
import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from .service import STTService

router = APIRouter(prefix="/stt", tags=["Speech-to-Text"])

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    service: STTService = Depends(STTService)
):
    await websocket.accept()
    session_id, vito_ws = await service.create_session(websocket)
    
    try:
        await asyncio.gather(
            handle_client_to_vito(websocket, service, session_id),
            handle_vito_to_client(vito_ws, service, session_id)
        )
    except WebSocketDisconnect:
        pass
    finally:
        await service.remove_session(session_id)


async def handle_client_to_vito(websocket: WebSocket, service: STTService, session_id: str):
    try:
        while True:
            chunk = await websocket.receive_bytes()
            await service.stream_audio_chunk(session_id, chunk)
    except WebSocketDisconnect:
        pass


async def handle_vito_to_client(vito_ws, service: STTService, session_id: str):
    try:
        async for msg in vito_ws:
            try:
                result = json.loads(msg)
                if "alternatives" in result and result["alternatives"] and result["final"]:
                    text = result["alternatives"][0]["text"]
                    await service.send_text(session_id, text)
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"Message parsing error: {e}")
    except Exception as e:
        print(f"Vito connection error: {e}")