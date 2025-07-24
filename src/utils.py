from functools import wraps
from typing import Callable, Any, Awaitable, TypeVar, ParamSpec
from src.exceptions import VoiceCommandException, VoiceCommandErrorCode

P = ParamSpec('P')
T = TypeVar('T')

def voice_command_error(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> T:
        session_id = kwargs.get('session_id') if 'session_id' in kwargs else (args[0] if args else None)
        try:
            return await func(self, *args, **kwargs) # type: ignore
        except VoiceCommandException as e:
            if hasattr(self, 'user_session_service') and session_id:
                try:
                    await self.user_session_service.send_error(session_id, e)
                except Exception:
                    pass  # 에러 전송 실패 시 무시
            raise VoiceCommandException(
                VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR
            ) from e
        except Exception as e:
            if hasattr(self, 'user_session_service') and session_id:
                try:
                    await self.user_session_service.send_error(session_id, e)
                except Exception:
                    pass  # 에러 전송 실패 시 무시
            raise VoiceCommandException(
                VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR
            ) from e
    
    return wrapper # type: ignore