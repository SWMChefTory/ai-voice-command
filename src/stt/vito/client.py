# src/stt/streaming/service.py
import asyncio
import time
import websockets
import logging
from requests import Session
from typing import Any, Dict, Optional, cast
from .config import vito_config



class VitoStreamingClient:
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._sess = Session()
        self._token: Optional[Dict[str, Any]] = None
        self._lock = asyncio.Lock()
        self.sample_rate = vito_config.sample_rate

    async def _access_token(self) -> Dict[str, Any]:
        async with self._lock:
            if (
                self._token is None
                or self._token.get("expire_at", 0) < time.time()
            ):
                loop = asyncio.get_event_loop()
                resp = await loop.run_in_executor(
                    None,
                    lambda: self._sess.post(
                        f"{vito_config.api_base}/v1/authenticate",
                        data={
                            "client_id": vito_config.client_id,
                            "client_secret": vito_config.client_secret,
                        },
                    )
                )
                resp.raise_for_status()
                self._token = resp.json()
            assert self._token is not None 
            return self._token

    async def connect(self) -> websockets.ClientConnection:
        token = await self._access_token()
        qs = dict(
                sample_rate=str(vito_config.sample_rate),
                encoding=vito_config.encoding,
                use_itn=vito_config.use_itn,
                use_disfluency_filter=vito_config.use_disfluency_filter,
                use_profanity_filter=vito_config.use_profanity_filter,
            )
        uri = "wss://{}/v1/transcribe:streaming?{}".format(
            vito_config.api_base.split("://")[1], "&".join(map("=".join, qs.items()))
        )
        hdr = {"Authorization": f"bearer {token['access_token']}"}
        try:
            return await websockets.connect(uri, additional_headers=hdr)
        except Exception as e:
            print(e)
            raise e

    async def send_chunk(self, ws: websockets.ClientConnection, chunk: bytes):
        await ws.send(chunk)

    async def close(self, ws: websockets.ClientConnection):
        await ws.close()