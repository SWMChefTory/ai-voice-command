# tests/stt/test_service.py
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
import websockets

from src.stt.service import STTService
from src.stt.client import STTClient
from src.stt.repository import STTSessionRepository
from src.stt.exceptions import STTException, STTErrorCode


class TestSTTService:
    """STT 서비스 동작을 설명한다"""
    
    @pytest.fixture
    def mock_repository(self):
        return Mock(spec=STTSessionRepository)
    
    @pytest.fixture
    def mock_client(self):
        return AsyncMock(spec=STTClient)
    
    @pytest.fixture
    def mock_websocket(self):
        return AsyncMock(spec=websockets.ClientConnection)
    
    @pytest.fixture
    def service(self, mock_repository, mock_client):
        return STTService(mock_repository, mock_client)
    
    @pytest.fixture
    def session_id(self):
        return "test-session-123"
    
    @pytest.fixture
    def audio_chunk(self):
        return b"fake_audio_data"

    @staticmethod
    def setup_mock_get_result(mock_client, messages):
        """client.get_result mock을 설정하는 헬퍼 메서드"""
        async def mock_async_iterator():
            for message in messages:
                yield message
        
        mock_client.get_result.return_value = mock_async_iterator()

    @staticmethod
    async def collect_service_results(service, session_id):
        """service.get_result의 출력을 수집하는 헬퍼 메서드"""
        results = []
        async for result in service.get_result(session_id):
            results.append(result)
        return results

    class GivenConnect:
        """웹소켓 연결을 해야 할 때"""

        class WhenConnectSucceeds:
            """연결이 성공한다면"""
            
            @pytest.mark.asyncio
            async def then_should_create_session(self, service, mock_client, mock_repository, mock_websocket, session_id):
                """세션을 생성해야한다"""
                mock_client.connect.return_value = mock_websocket
                
                await service.connect(session_id)
                
                mock_client.connect.assert_called_once()
                mock_repository.create_session.assert_called_once_with(session_id, mock_websocket)

        class WhenConnectFails:
            """연결이 실패한다면"""
            
            @pytest.mark.asyncio
            async def then_should_raise_service_error(self, service, mock_client, session_id):
                """서비스 오류를 발생시켜야한다"""
                original_exception = STTException(STTErrorCode.STT_CONNECTION_ERROR, Exception("Connection failed"))
                mock_client.connect.side_effect = original_exception
                
                with pytest.raises(STTException) as exc_info:
                    await service.connect(session_id)
                
                assert exc_info.value.code == STTErrorCode.STT_SERVICE_ERROR
                assert exc_info.value.original_exception == original_exception

    class GivenStreamAudio:
        """오디오를 스트리밍해야 할 때"""

        class WhenSessionExists:
            """세션이 존재한다면"""
            
            @pytest.mark.asyncio
            async def then_should_send_chunk_to_existing_session(self, service, mock_client, mock_repository, mock_websocket, session_id, audio_chunk):
                """기존 세션으로 청크를 전송해야한다"""
                mock_repository.is_session_exists.return_value = True
                mock_repository.find_session.return_value = mock_websocket
                
                await service.stream_audio(session_id, audio_chunk)
                
                mock_repository.is_session_exists.assert_called_once_with(session_id)
                mock_repository.find_session.assert_called_once_with(session_id)
                mock_client.send_chunk.assert_called_once_with(mock_websocket, audio_chunk)

        class WhenSessionNotExists:
            """세션이 존재하지 않는다면"""
            
            @pytest.mark.asyncio
            async def then_should_reconnect_and_send_chunk(self, service, mock_client, mock_repository, mock_websocket, session_id, audio_chunk):
                """재연결 후 청크를 전송해야한다"""
                mock_repository.is_session_exists.return_value = False
                mock_client.connect.return_value = mock_websocket
                mock_repository.find_session.return_value = mock_websocket
                
                await service.stream_audio(session_id, audio_chunk)
                
                mock_client.connect.assert_called_once()
                mock_repository.create_session.assert_called_once_with(session_id, mock_websocket)
                mock_client.send_chunk.assert_called_once_with(mock_websocket, audio_chunk)

        class WhenClientSendFails:
            """클라이언트 전송이 실패한다면"""
            
            @pytest.mark.asyncio
            async def then_should_raise_service_error(self, service, mock_client, mock_repository, mock_websocket, session_id, audio_chunk):
                """서비스 오류를 발생시켜야한다"""
                mock_repository.is_session_exists.return_value = True
                mock_repository.find_session.return_value = mock_websocket
                mock_client.send_chunk.side_effect = Exception("Send failed")
                
                with pytest.raises(STTException) as exc_info:
                    await service.stream_audio(session_id, audio_chunk)
                
                assert exc_info.value.code == STTErrorCode.STT_SERVICE_ERROR

    class GivenDisconnect:
        """연결을 해제해야 할 때"""

        class WhenSessionExists:
            """세션이 존재한다면"""
            
            @pytest.mark.asyncio
            async def then_should_close_connection_and_remove_session(self, service, mock_client, mock_repository, mock_websocket, session_id):
                """연결을 종료하고 세션을 제거해야한다"""
                mock_repository.is_session_exists.return_value = True
                mock_repository.find_session.return_value = mock_websocket
                
                await service.disconnect(session_id)
                
                mock_repository.is_session_exists.assert_called_once_with(session_id)
                mock_repository.find_session.assert_called_once_with(session_id)
                mock_client.close.assert_called_once_with(mock_websocket)
                mock_repository.remove_session.assert_called_once_with(session_id)

        class WhenSessionNotExists:
            """세션이 존재하지 않는다면"""
            
            @pytest.mark.asyncio
            async def then_should_do_nothing(self, service, mock_client, mock_repository, session_id):
                """아무것도 하지 않아야한다"""
                mock_repository.is_session_exists.return_value = False
                
                await service.disconnect(session_id)
                
                mock_repository.is_session_exists.assert_called_once_with(session_id)
                mock_repository.find_session.assert_not_called()
                mock_client.close.assert_not_called()
                mock_repository.remove_session.assert_not_called()

    class GivenGetResult:
        """STT 결과를 받아야 할 때"""

        class WhenSessionExists:
            """세션이 존재한다면"""
            
            @pytest.mark.asyncio
            async def then_should_yield_results_and_cleanup(self, service, mock_client, mock_repository, mock_websocket, session_id):
                """결과를 반환하고 정리해야한다"""
                mock_repository.is_session_exists.return_value = True
                mock_repository.find_session.return_value = mock_websocket
                TestSTTService.setup_mock_get_result(mock_client, ["안녕하세요", "감사합니다"])
                
                results = await TestSTTService.collect_service_results(service, session_id)
                
                assert len(results) == 2
                assert results[0] == "안녕하세요"
                assert results[1] == "감사합니다"
                
                mock_client.get_result.assert_called_once_with(mock_websocket)
                mock_client.close.assert_called_once_with(mock_websocket)
                mock_repository.remove_session.assert_called_once_with(session_id)

        class WhenSessionNotExists:
            """세션이 존재하지 않는다면"""
            
            @pytest.mark.asyncio
            async def then_should_yield_nothing(self, service, mock_repository, session_id):
                """아무것도 반환하지 않아야한다"""
                mock_repository.is_session_exists.return_value = False
                
                results = await TestSTTService.collect_service_results(service, session_id)
                
                assert len(results) == 0
                mock_repository.find_session.assert_not_called()

        class WhenConnectionClosed:
            """연결이 끊어진다면"""
            
            @pytest.mark.asyncio
            async def then_should_handle_exception_and_cleanup(self, service, mock_client, mock_repository, mock_websocket, session_id):
                """예외를 처리하고 정리해야한다"""
                mock_repository.is_session_exists.return_value = True
                mock_repository.find_session.return_value = mock_websocket
                
                async def mock_get_result_with_exception(websocket):
                    yield "첫 번째 결과"
                    raise websockets.ConnectionClosed(None, None)
                
                mock_client.get_result.return_value = mock_get_result_with_exception(mock_websocket)
                
                results = await TestSTTService.collect_service_results(service, session_id)
                
                assert len(results) == 1
                assert results[0] == "첫 번째 결과"
                
                mock_client.close.assert_called_once_with(mock_websocket)
                mock_repository.remove_session.assert_called_once_with(session_id)
