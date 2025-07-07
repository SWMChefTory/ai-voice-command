import asyncio
from asyncio.log import logger
from fastapi import APIRouter, Depends, WebSocket

from src.deps import voice_command_service
from src.service import VoiceCommandService


router = APIRouter(prefix="/stt", tags=["Speech-to-Text"])

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    voice_command_service: VoiceCommandService = Depends(voice_command_service),
):
    await websocket.accept()
    session_id = await voice_command_service.create_session(websocket)

    try:
        await asyncio.gather(
            _client_to_stt(websocket, voice_command_service, session_id),
            _stt_to_intent_to_client(voice_command_service, session_id),
        )
    except Exception as e:
        logger.error(f"[VoiceCommandRouter] {e}", exc_info=True)
    finally:
        await voice_command_service.disconnect(session_id)

async def _client_to_stt(ws: WebSocket,
                         service: VoiceCommandService,
                         session_id: str):
    async for chunk in ws.iter_bytes():
        await service.create_recognition(session_id, chunk)

async def _stt_to_intent_to_client(service: VoiceCommandService, session_id: str):
    await service.create_intent(session_id)