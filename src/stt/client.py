from abc import ABC, abstractmethod
import asyncio
import base64
import json
import time
from grpc.aio import StreamStreamCall
from requests import Session
from typing import Any, AsyncIterator, Dict, Optional, AsyncGenerator

from uvicorn.main import logger
import websockets
from websockets.asyncio.client import ClientConnection
from websockets.protocol import State
import grpc
import nest_pb2 as nest_pb2 
import nest_pb2_grpc as nest_pb2_grpc

from src.stt.exceptions import NaverClovaStreamingClientException, OpenAIStreamingClientException, VitoStreamingClientException, STTErrorCode

from .config import vito_config, naver_clova_config, openai_config

class STTClient(ABC):
    @abstractmethod
    async def connect_session(self) -> Any:
        pass

    @abstractmethod
    async def close_session(self, connection: Any):
        pass

    @abstractmethod
    async def send_chunk(self, connection: Any, chunk: bytes):
        pass

    @abstractmethod
    async def receive_result(self, connection: Any) -> AsyncIterator[str]:
        yield ""
    


class VitoStreamingClient(STTClient):
    def __init__(self):
        super().__init__()
        self._sess = Session()
        self._token: Optional[Dict[str, Any]] = None
        self._lock = asyncio.Lock()
        self._config = vito_config

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
                            f"{self._config.api_base}/v1/authenticate",
                            data={
                                "client_id": self._config.client_id,
                                "client_secret": self._config.client_secret,
                            },
                        )
                    )
                    resp.raise_for_status()
                    self._token = resp.json()
                    if self._token is None:
                        logger.error("access_token is None")
                        raise VitoStreamingClientException(STTErrorCode.STT_CONNECTION_ERROR)
                except Exception as e:
                    logger.error(e)
                    raise VitoStreamingClientException(STTErrorCode.STT_CONNECTION_ERROR)
            return self._token

    async def connect_session(self) -> ClientConnection:
        token = await self._access_token()
        query_params = dict(
            sample_rate=str(self._config.sample_rate),
            encoding=self._config.encoding,
            use_itn=self._config.use_itn,
            use_disfluency_filter=self._config.use_disfluency_filter,
            use_profanity_filter=self._config.use_profanity_filter,
            model_name=self._config.model_name,
            keywords=self._config.keywords,
            keywords_boost=str(self._config.keywords_boost),
            domain=self._config.domain,
        )
        params = "&".join(f"{k}={v}" for k, v in query_params.items())
        uri = f"wss://{self._config.api_base.split('://')[1]}/v1/transcribe:streaming?{params}"
        hdr = {"Authorization": f"bearer {token['access_token']}"}
        try:
            return await websockets.connect(uri, additional_headers=hdr)
        except Exception as e:
            logger.error(e)
            raise VitoStreamingClientException(STTErrorCode.STT_CONNECTION_ERROR)

    async def close_session(self, connection: ClientConnection):
        if connection.state == State.CLOSED:
            return
        await connection.close()

    async def send_chunk(self, connection: ClientConnection, chunk: bytes):
        try:
            await connection.send(chunk)
        except Exception as e:
            logger.error(e)
            raise VitoStreamingClientException(STTErrorCode.STT_STREAM_ERROR)

    async def receive_result(self, connection: ClientConnection) -> AsyncIterator[str]:
        async for msg in connection:
            data = json.loads(msg)
            if not data.get("final"):
                continue
            if not data.get("alternatives"):
                continue
            yield data["alternatives"][0]["text"] 


class NaverClovaStreamingClient(STTClient):
    def __init__(self):
        super().__init__()
        self._sess = Session()
        self._token = None
        self._lock = asyncio.Lock()
        self._config = naver_clova_config

    async def connect_session(self) -> StreamStreamCall: # type: ignore
        try:
            creds = grpc.ssl_channel_credentials() # type: ignore
            channel = grpc.aio.secure_channel(self._config.grpc_server, creds) # type: ignore
            stub = nest_pb2_grpc.NestServiceStub(channel)
            
            metadata = (("authorization", f"Bearer {self._config.access_token}"),)
            
            call = stub.recognize(metadata=metadata) # type: ignore
            
            config_json = {
                "transcription": {
                    "language": self._config.language
                },
                "semanticEpd": {
                    "skipEmptyText": self._config.skip_empty_text,  
                    "useWordEpd": self._config.use_word_epd,
                    "usePeriodEpd": self._config.use_period_epd,
                    "gapThreshold": self._config.gap_threshold,
                    "durationThreshold": self._config.duration_threshold,
                }
            }
            
            config_request = nest_pb2.NestRequest( # type: ignore
                type=nest_pb2.RequestType.CONFIG, # type: ignore
                config=nest_pb2.NestConfig(config=json.dumps(config_json)) # type: ignore
            )
            
            await call.write(config_request) # type: ignore
            
            return call # type: ignore
            
        except Exception as e:
            logger.error(e)
            raise NaverClovaStreamingClientException(STTErrorCode.STT_CONNECTION_ERROR)

    async def send_chunk(self, connection: StreamStreamCall, chunk: bytes): # type: ignore
        try:
            data_request = nest_pb2.NestRequest( # type: ignore
                type=nest_pb2.RequestType.DATA, # type: ignore
                data=nest_pb2.NestData(chunk=chunk) # type: ignore
            )
            await connection.write(data_request) # type: ignore
        except Exception as e:
            logger.error(e)
            raise NaverClovaStreamingClientException(STTErrorCode.STT_STREAM_ERROR)

    async def receive_result(self, connection: StreamStreamCall) -> AsyncIterator[str]: # type: ignore
        try:
            async for response in connection: # type: ignore
                if response.contents: # type: ignore
                    try:
                        result_data = json.loads(response.contents) # type: ignore
                        if "transcription" in result_data:
                            text = result_data["transcription"].get("text", "")
                            if text and text != " ":
                                yield text
                    except json.JSONDecodeError:
                        yield response.contents # type: ignore
        except Exception as e:
            logger.error(e)
            raise NaverClovaStreamingClientException(STTErrorCode.STT_STREAM_ERROR)

    async def close_session(self, connection: StreamStreamCall): # type: ignore 
        try:
            if connection:
                await connection.done_writing() # type: ignore
                channel = connection._channel if hasattr(connection, '_channel') else None # type: ignore
                if channel:
                    await channel.close() # type: ignore
        except Exception as e:
            logger.error(e)


class OpenAIStreamingClient(STTClient):
    def __init__(self):
        super().__init__()
        self._lock = asyncio.Lock()
        self._config = openai_config

    async def connect_session(self) -> ClientConnection:
        uri = self._config.api_base
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "OpenAI-Beta": "realtime=v1",
        }
        try:
            ws: ClientConnection = await websockets.connect(uri, additional_headers=headers)

            create_msg: Dict[str, Any] = {
                "type": "transcription_session.update",
                "session": {
                    "input_audio_format": self._config.input_audio_format,
                    "input_audio_transcription": {
                        "model": self._config.model,
                        "prompt": "",
                        "language": self._config.language
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": self._config.vad_threshold,
                        "prefix_padding_ms": self._config.prefix_padding_ms,
                        "silence_duration_ms": self._config.silence_duration_ms,
                    },
                    "input_audio_noise_reduction": {
                        "type": self._config.noise_reduction_type
                    },
                    "include": [ 
                        "item.input_audio_transcription.logprobs",
                    ],
                }
            }
            await ws.send(json.dumps(create_msg))
            return ws
        except Exception as e:
            logger.error(e)
            raise OpenAIStreamingClientException(STTErrorCode.STT_CONNECTION_ERROR)

    async def close_session(self, connection: ClientConnection):
        if connection.state != State.CLOSED:
            await connection.close()

    async def send_chunk(self, connection: ClientConnection, chunk: bytes):
        try:
            await connection.send(
                json.dumps(
                    {
                        "type": "input_audio_buffer.append",
                        "audio": base64.b64encode(chunk).decode("ascii"),
                    }
                )
            )
        except Exception as e:
            logger.error(e)
            raise OpenAIStreamingClientException(STTErrorCode.STT_STREAM_ERROR)

    async def receive_result(
        self, connection: ClientConnection
    ) -> AsyncGenerator[str, None]:
        async for msg in connection:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                continue
            
            msg_type = data.get("type")
            if msg_type == "conversation.item.input_audio_transcription.completed":
                transcript = data.get("transcript", "")
                if transcript:
                    yield transcript