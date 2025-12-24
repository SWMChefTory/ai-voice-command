import asyncio
from uvicorn.main import logger
from fastapi import APIRouter, Depends, Query, WebSocket
from uuid import UUID

from src.deps import voice_command_service
from src.exceptions import VoiceCommandException
from src.service import VoiceCommandService
from src.enums import STTProvider
from src.context import country_code_ctx, normalize_country_code

router = APIRouter(prefix="/voice-command", tags=["Voice Command"])

@router.websocket("/ws")
async def websocket_endpoint(
    client_websocket: WebSocket,
    provider: STTProvider = Query(),
    recipe_id: UUID = Query(),
    token: str = Query(),
    voice_command_service: VoiceCommandService = Depends(voice_command_service),
):
    session_id = None

    raw_country_code = client_websocket.headers.get("X-Country-Code")
    country_code_ctx.set(normalize_country_code(raw_country_code))

    await client_websocket.accept()
    
    try:
        user_id = await voice_command_service.validate_auth_token(token)
    except VoiceCommandException as e:
        logger.error(f"토큰 검증 실패: {e.code}")
        await client_websocket.close(code=1008, reason=str(e.code))
        return

    session_id = await voice_command_service.start_session(client_websocket, provider, user_id, recipe_id)

    try:
        await asyncio.gather(
            _process_stt_results(client_websocket, voice_command_service, session_id),
            _handle_recognition_flow(voice_command_service, session_id),
        )
    except ConnectionAbortedError:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(e)
    finally:
        await voice_command_service.end_session(session_id)

#유저 인터페이스로부터 받은 음성을 받아서 지속적으로 클라우드 STT에 전달. 메서드명 passAudioToSTT는 어떤가요?
async def _process_stt_results(
    client_websocket: WebSocket,
    service: VoiceCommandService,
    session_id: UUID
):
    logger.info(f"[Router] STT 결과 처리 시작 - 세션 ID: {session_id}")
    try:
        message_count = 0
        async for message in client_websocket.iter_bytes():
            message_count += 1
            if len(message) == 0:
                continue
                
            is_final = bool(message[0])
            audio_data = message[1:]
            await service.stream_audio(session_id, audio_data, is_final)
        raise ConnectionAbortedError("WebSocket connection closed")

    except Exception as e:
        raise e

#STT결과를 받고 의도 분류 후 유저 인터페이스로 전달
async def _handle_recognition_flow(service: VoiceCommandService, session_id: UUID):
    try:
        await service.stream_intents(session_id)
    except Exception as e:
        raise e