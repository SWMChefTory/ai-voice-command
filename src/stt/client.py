

from abc import ABC, abstractmethod
import json
from uvicorn.main import logger
from websockets import ClientConnection, State

from src.stt.exceptions import _VitoStreamingClientException, STTErrorCode
import asyncio
import time
from requests import Session
from typing import Any, AsyncIterator, Dict, Optional, AsyncGenerator
import websockets

from .config import vito_config

class STTClient(ABC):
    @abstractmethod
    async def connect(self) -> ClientConnection:
        pass

    @abstractmethod
    async def close(self, client_websocket: ClientConnection):
        pass

    @abstractmethod
    async def send_chunk(self, client_websocket: ClientConnection, chunk: bytes):
        pass

    @abstractmethod
    async def get_result(self, client_websocket: ClientConnection) -> AsyncIterator[str]:
        yield ""

class VitoStreamingClient(STTClient):
    def __init__(self):
        super().__init__()
        self._sess = Session()
        self._token: Optional[Dict[str, Any]] = None
        self._lock = asyncio.Lock()

    async def _access_token(self) -> Dict[str, Any]:
        async with self._lock:
            if (
                self._token is None
                or self._token.get("expire_at", 0) < time.time()
            ):
                try:
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

                    if self._token is None:
                        raise _VitoStreamingClientException(STTErrorCode.STT_CONNECTION_ERROR, ValueError("access_token is None"))
                except Exception as e:
                    raise _VitoStreamingClientException(STTErrorCode.STT_CONNECTION_ERROR, e)
            return self._token

    async def connect(self) -> ClientConnection:
        token = await self._access_token()
        query_params = dict(
                sample_rate=str(vito_config.sample_rate),
                encoding=vito_config.encoding,
                use_itn=vito_config.use_itn,
                use_disfluency_filter=vito_config.use_disfluency_filter,
                use_profanity_filter=vito_config.use_profanity_filter,
                model_name=vito_config.model_name,
                keywords=vito_config.keywords,
                keywords_boost=vito_config.keywords_boost,
                domain=vito_config.domain,
            )
        params = "&".join(f"{k}={v}" for k, v in query_params.items())
        uri = f"wss://{vito_config.api_base.split('://')[1]}/v1/transcribe:streaming?{params}"
        hdr = {"Authorization": f"bearer {token['access_token']}"}
        try:
            return await websockets.connect(uri, additional_headers=hdr)
        except Exception as e:
            raise _VitoStreamingClientException(STTErrorCode.STT_CONNECTION_ERROR, e)

    async def close(self, client_websocket: ClientConnection):
        logger.info(f"[VitoStreamingClient] 연결 상태: {client_websocket.state}")
        if client_websocket.state == State.CLOSED:
            return
        await client_websocket.close()

    async def send_chunk(self, client_websocket: ClientConnection, chunk: bytes):
        try:
            await client_websocket.send(chunk)
        except Exception as e:
            raise _VitoStreamingClientException(STTErrorCode.STT_STREAM_ERROR, e)

    async def get_result(self, client_websocket: ClientConnection) -> AsyncIterator[str]:
        async for msg in client_websocket:
            data = json.loads(msg)
            if not data.get("final"):
                continue
            if not data.get("alternatives"):
                continue
            yield data["alternatives"][0]["text"] 