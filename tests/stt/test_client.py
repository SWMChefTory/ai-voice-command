# tests/stt/test_client.py
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from websockets import State
from requests import Response

from src.stt.client import VitoStreamingClient
from src.stt.exceptions import _VitoStreamingClientException, STTErrorCode


class TestVitoStreamingClient:
    """VITO 스트리밍 클라이언트 동작을 설명한다"""
    
    @pytest.fixture
    def client(self):
        return VitoStreamingClient()

    @pytest.fixture
    def mock_websocket(self):
        mock = AsyncMock()
        mock.state = State.OPEN
        return mock

    @pytest.fixture
    def mock_response(self):
        mock = Mock(spec=Response)
        mock.json.return_value = {
            "access_token": "test-access-token",
            "expire_at": 9999999999
        }
        mock.raise_for_status.return_value = None
        return mock

    @staticmethod
    def setup_mock_websocket_messages(mock_websocket, messages):
        """웹소켓 mock에 메시지들을 설정하는 헬퍼 메서드"""
        async def mock_async_iterator():
            for message in messages:
                yield message
        
        mock_websocket.__aiter__ = lambda self: mock_async_iterator()

    @staticmethod
    async def collect_get_result_output(client, mock_websocket):
        """get_result의 출력을 수집하는 헬퍼 메서드"""
        results = []
        async for result in client.get_result(mock_websocket):
            results.append(result)
        return results

    class GivenAccessToken:
        """액세스 토큰을 획득해야 할 때"""

        @pytest.fixture
        def expired_token(self):
                return {
                    "access_token": "expired-token",
                    "expire_at": 0
                }

        class WhenTokenDoesNotExist:
            """토큰이 존재하지 않는다면"""
            
            @pytest.mark.asyncio
            async def then_should_fetch_new_token(self, client, mock_response):
                """새로운 토큰을 요청해야한다"""
                with patch.object(client._sess, 'post', return_value=mock_response):
                    token = await client._access_token()
                    
                    assert token["access_token"] == "test-access-token"
                    assert client._token is not None

        class WhenTokenIsExpired:
            """토큰이 만료되었다면"""
            
            @pytest.mark.asyncio
            async def then_should_fetch_new_token(self, client, mock_response, expired_token):
                """새로운 토큰을 요청해야한다"""
                client._token = expired_token
                
                with patch.object(client._sess, 'post', return_value=mock_response):
                    token = await client._access_token()
                    
                    assert token["access_token"] == "test-access-token"
                    assert client._token["access_token"] == "test-access-token"

        class WhenTokenRequestFails:
            """토큰 요청이 실패한다면"""
            
            @pytest.mark.asyncio
            async def then_should_raise_connection_error(self, client):
                """연결 오류를 발생시켜야한다"""
                mock_error_response = Mock()
                mock_error_response.raise_for_status.side_effect = Exception("API Error")
                
                with patch.object(client._sess, 'post', return_value=mock_error_response):
                    with pytest.raises(_VitoStreamingClientException) as exc_info:
                        await client._access_token()
                    
                    assert exc_info.value.code == STTErrorCode.STT_CONNECTION_ERROR

    class GivenConnect:
        """웹소켓 연결을 해야 할 때"""

        @pytest.fixture
        def valid_token(self):
            return {
                "access_token": "test-access-token",
                "expire_at": 9999999999
            }

        class WhenConnectionSucceeds:
            """연결이 성공한다면"""
            
            @pytest.mark.asyncio
            async def then_should_return_websocket_connection(self, client, mock_websocket, valid_token):
                
                """웹소켓 연결을 반환해야한다"""
                with patch.object(client, '_access_token', return_value=valid_token):
                    with patch('websockets.connect', new=AsyncMock(return_value=mock_websocket)):
                        connection = await client.connect()
                        
                        assert connection == mock_websocket

        class WhenConnectionFails:
            """연결이 실패한다면"""
            
            @pytest.mark.asyncio
            async def then_should_raise_connection_error(self, client, valid_token):
                """연결 오류를 발생시켜야한다"""
                with patch.object(client, '_access_token', return_value=valid_token):
                    with patch('websockets.connect', side_effect=Exception("Connection failed")):
                        with pytest.raises(_VitoStreamingClientException) as exc_info:
                            await client.connect()
                        
                        assert exc_info.value.code == STTErrorCode.STT_CONNECTION_ERROR

    class GivenClose:
        """웹소켓 연결을 종료해야 할 때"""

        class WhenConnectionIsOpen:
            """연결이 열려있다면"""
            
            @pytest.mark.asyncio
            async def then_should_close_connection(self, client, mock_websocket):
                """연결을 종료해야한다"""
                mock_websocket.state = State.OPEN
                
                await client.close(mock_websocket)
                
                mock_websocket.close.assert_called_once()

        class WhenConnectionIsAlreadyClosed:
            """연결이 이미 종료되었다면"""
            
            @pytest.mark.asyncio
            async def then_should_not_call_close(self, client, mock_websocket):
                """close를 호출하지 않아야한다"""
                mock_websocket.state = State.CLOSED
                
                await client.close(mock_websocket)
                
                mock_websocket.close.assert_not_called()

    class GivenSendChunk:
        """오디오 청크를 전송해야 할 때"""

        @pytest.fixture
        def audio_chunk(self):
            return b"fake_audio_data"

        class WhenSendSucceeds:
            """전송이 성공한다면"""
            
            @pytest.mark.asyncio
            async def then_should_send_chunk_to_websocket(self, client, mock_websocket, audio_chunk):
                """웹소켓으로 청크를 전송해야한다"""
                mock_websocket.send = AsyncMock()
                
                await client.send_chunk(mock_websocket, audio_chunk)
                
                mock_websocket.send.assert_called_once_with(audio_chunk)

        class WhenSendFails:
            """전송이 실패한다면"""
            
            @pytest.mark.asyncio
            async def then_should_raise_stream_error(self, client, mock_websocket, audio_chunk):
                """스트림 오류를 발생시켜야한다"""
                mock_websocket.send = AsyncMock(side_effect=Exception("Send failed"))
                
                with pytest.raises(_VitoStreamingClientException) as exc_info:
                    await client.send_chunk(mock_websocket, audio_chunk)
                
                assert exc_info.value.code == STTErrorCode.STT_STREAM_ERROR

    class GivenGetResult:
        """STT 결과를 받아야 할 때"""

        @pytest.fixture
        def final_message(self):
            return json.dumps({
                "final": True,
                "alternatives": [{"text": "안녕하세요"}]
            })

        @pytest.fixture
        def non_final_message(self):
            return json.dumps({
                "final": False,
                "alternatives": [{"text": "안녕"}]
            })

        @pytest.fixture
        def empty_alternatives_message(self):
            return json.dumps({
                "final": True,
                "alternatives": []
            })

        class WhenReceivingFinalMessage:
            """최종 메시지를 받는다면"""
            
            @pytest.mark.asyncio
            async def then_should_yield_text_result(self, client, mock_websocket, final_message):
                """텍스트 결과를 반환해야한다"""
                TestVitoStreamingClient.setup_mock_websocket_messages(mock_websocket, [final_message])
                
                results = await TestVitoStreamingClient.collect_get_result_output(client, mock_websocket)
                
                assert len(results) == 1
                assert results[0] == "안녕하세요"

        class WhenReceivingNonFinalMessage:
            """중간 메시지를 받는다면"""
            
            @pytest.mark.asyncio
            async def then_should_not_yield_result(self, client, mock_websocket, non_final_message):
                """결과를 반환하지 않아야한다"""
                TestVitoStreamingClient.setup_mock_websocket_messages(mock_websocket, [non_final_message])
                
                results = await TestVitoStreamingClient.collect_get_result_output(client, mock_websocket)
                
                assert len(results) == 0

        class WhenReceivingEmptyAlternatives:
            """빈 대안 메시지를 받는다면"""
            
            @pytest.mark.asyncio
            async def then_should_not_yield_result(self, client, mock_websocket, empty_alternatives_message):
                """결과를 반환하지 않아야한다"""
                TestVitoStreamingClient.setup_mock_websocket_messages(mock_websocket, [empty_alternatives_message])

                results = await TestVitoStreamingClient.collect_get_result_output(client, mock_websocket)
                
                assert len(results) == 0

        class WhenReceivingMultipleMessages:
            """여러 메시지를 받는다면"""
            
            @pytest.mark.asyncio
            async def then_should_yield_only_final_results(self, client, mock_websocket, 
                                                         final_message, non_final_message, 
                                                         empty_alternatives_message):
                """최종 결과만 반환해야한다"""
                final_message2 = json.dumps({
                    "final": True,
                    "alternatives": [{"text": "감사합니다"}]
                })
                
                messages = [non_final_message, final_message, empty_alternatives_message, final_message2]
                TestVitoStreamingClient.setup_mock_websocket_messages(mock_websocket, messages)
                
                results = await TestVitoStreamingClient.collect_get_result_output(client, mock_websocket)
                
                assert len(results) == 2
                assert results[0] == "안녕하세요"
                assert results[1] == "감사합니다"  