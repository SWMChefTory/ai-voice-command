import asyncio
from asyncio.log import logger
from fastapi import APIRouter, Depends, WebSocket

from src.deps import voice_command_service
from src.service import VoiceCommandService


router = APIRouter(prefix="/voice-command", tags=["Voice Command"])

@router.websocket("/ws")
async def websocket_endpoint(
    client_websocket: WebSocket,
    voice_command_service: VoiceCommandService = Depends(voice_command_service),
):
    await client_websocket.accept()
    session_id = await voice_command_service.initialize_session(client_websocket)

    try:
        await asyncio.gather(
            _process_stt_results(client_websocket, voice_command_service, session_id),
            _handle_recognition_flow(voice_command_service, session_id),
        )
    except Exception as e:
        logger.error(f"[VoiceCommandRouter] {e}", exc_info=True)
    finally:
        await voice_command_service.disconnect(session_id)

async def _process_stt_results(client_websocket: WebSocket,
                         service: VoiceCommandService,
                         session_id: str):
    async for chunk in client_websocket.iter_bytes():
        await service.process_stt_results(session_id, chunk)

async def _handle_recognition_flow(service: VoiceCommandService, session_id: str):
    await service.process_intents(session_id)