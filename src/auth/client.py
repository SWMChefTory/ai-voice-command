from abc import ABC, abstractmethod
import httpx
from uvicorn.main import logger
from src.auth.exception import AuthErrorCode, AuthException
from .config import auth_config
from uuid import UUID
class AuthClient(ABC):
    @abstractmethod
    async def validate_auth_token(self, auth_token: str) -> UUID:
        pass

class CheftoryAuthClient(AuthClient):
    def __init__(self):
        super().__init__()
        self._config = auth_config

    async def validate_auth_token(self, auth_token: str) -> UUID:
        url = f"{self._config.api_base}/papi/v1/auth/extract-user-id"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {auth_token}"},
                    timeout=5.0
                )

                if response.status_code == 200:
                    data = response.json()
                    user_id = data.get("userId")
                    return user_id
                else:
                    error_data = response.json()
                    error_code = error_data.get("errorCode")

                    code_map = {
                        "AUTH_1": AuthErrorCode.INVALID_TOKEN,
                        "AUTH_2": AuthErrorCode.EXPIRED_TOKEN,
                        "AUTH_3": AuthErrorCode.INVALID_USER,
                    }

                    mapped_code = code_map.get(error_code, AuthErrorCode.INVALID_TOKEN)
                    raise AuthException(mapped_code)
                    
                    
        except httpx.RequestError as e:
            logger.error(e, exc_info=True)
            raise e