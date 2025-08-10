import asyncio
from asyncio.log import logger
from fastapi import APIRouter, Depends, Query, WebSocket
from uuid import UUID

from src.deps import voice_command_service
from src.service import VoiceCommandService
from src.models import STTProvider

router = APIRouter(prefix="/voice-command", tags=["Voice Command"])

@router.websocket("/ws")
async def websocket_endpoint(
    client_websocket: WebSocket,
    provider: STTProvider = Query(),
    recipe_id: UUID = Query(),
    token: str = Query(),
    voice_command_service: VoiceCommandService = Depends(voice_command_service),
):
    try:
        user_id = await voice_command_service.validate_auth_token(token)
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        await client_websocket.close(code=1008, reason="Unauthorized token")
        return
    
    await client_websocket.accept()

    session_id = await voice_command_service.start_session(client_websocket, provider, user_id, recipe_id)

    try:
        await asyncio.gather(
            _process_stt_results(client_websocket, voice_command_service, session_id),
            _handle_recognition_flow(voice_command_service, session_id),
        )
    except Exception as e:
        logger.error(e)
    finally:
        await voice_command_service.end_session(session_id)

async def _process_stt_results(client_websocket: WebSocket,
                         service: VoiceCommandService,
                         session_id: UUID):
    async for chunk in client_websocket.iter_bytes():
        await service.stream_audio(session_id, chunk)

async def _handle_recognition_flow(service: VoiceCommandService, session_id: UUID):
    await service.stream_intents(session_id)