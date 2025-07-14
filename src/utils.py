from functools import wraps

from src.exceptions import VoiceCommandErrorCode, VoiceCommandException


def voice_command_error(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        session_id = args[0] if args else None
        try:
            return await func(self, *args, **kwargs)
        except VoiceCommandException as e:
            await self.user_session_service.send_error(session_id, e)
            raise VoiceCommandException(
                VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e
            ) from e
        except Exception as e:
            await self.user_session_service.send_error(session_id, e)
            raise VoiceCommandException(
                VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e
            ) from e
    return wrapper