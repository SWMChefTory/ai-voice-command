from src.auth.client import AuthClient
from uuid import UUID

class AuthService:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

    async def validate_auth_token(self, auth_token: str) -> UUID:
        return await self.auth_client.validate_auth_token(auth_token)