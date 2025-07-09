# tests/test_stt_repository.py
import pytest
from unittest.mock import Mock
from websockets import ClientConnection
from src.stt.repository import STTSessionRepositoryImpl

class TestSTTSessionRepository:
    """STT 세션 레포지토리 동작을 설명한다"""
    
    @pytest.fixture
    def repository(self):
        return STTSessionRepositoryImpl()

    class GivenCreateSession:
        """세션을 생성해야 할 때"""

        @pytest.fixture
        def session_id(self):
            return "test-session-123"

        @pytest.fixture
        def mock_websocket(self):
            return Mock(spec=ClientConnection)

        @pytest.fixture
        def another_session_id(self):
            return "test-session-456"

        @pytest.fixture
        def another_mock_websocket(self):
            return Mock(spec=ClientConnection)
        
        class WhenCreateSession:
            """새로운 세션을 생성 해야한다면"""
            
            def then_should_store_session_with_websocket(self, repository, session_id, mock_websocket):
                """세션을 저장해야한다"""
                repository.create_session(session_id, mock_websocket)
                
                assert len(repository.sessions) == 1
                assert repository.sessions[session_id] == mock_websocket
        
        class WhenSessionAlreadyExists:
            """이미 존재하는 세션을 생성 해야한다면"""
            
            def then_should_overwrite_existing_session(self, repository, session_id, mock_websocket, another_mock_websocket):
                """기존 세션을 덮어써야한다"""
                repository.create_session(session_id, mock_websocket)
                assert repository.sessions[session_id] == mock_websocket
                
                repository.create_session(session_id, another_mock_websocket)
                
                assert repository.sessions[session_id] == another_mock_websocket
                assert len(repository.sessions) == 1

    class GivenRemoveSession:
        """세션을 제거해야 할 때"""

        @pytest.fixture
        def session_id(self):
            return "test-session-123"

        @pytest.fixture
        def mock_websocket(self):
            return Mock(spec=ClientConnection)

        @pytest.fixture
        def another_session_id(self):
            return "test-session-456"

        @pytest.fixture
        def another_mock_websocket(self):
            return Mock(spec=ClientConnection)

        class WhenSessionDoesExist:
            """세션이 존재 한다면"""
            
            def then_should_remove_session_successfully(self, repository, session_id, mock_websocket):
                """세션을 제거해야한다"""
                repository.create_session(session_id, mock_websocket)
                assert repository.is_session_exists(session_id)

                repository.remove_session(session_id)
                
                assert not repository.is_session_exists(session_id)
                assert len(repository.sessions) == 0

        class WhenSessionDoesNotExist:
            """세션이 존재하지 않는다면"""
            
            def then_should_not_raise_error(self, repository, session_id):
                """세션을 제거해야한다"""
                assert not repository.is_session_exists(session_id)
                
                repository.remove_session(session_id)
                
                assert len(repository.sessions) == 0
        
        class WhenMultipleSessionsExist:
            """여러 세션이 존재 한다면"""
            
            def then_should_remove_only_specified_session(self, repository, session_id, another_session_id, mock_websocket, another_mock_websocket):
                """세션을 제거해야한다"""
                repository.create_session(session_id, mock_websocket)
                repository.create_session(another_session_id, another_mock_websocket)
                assert len(repository.sessions) == 2
                
                repository.remove_session(session_id)
                
                assert not repository.is_session_exists(session_id)
                assert repository.is_session_exists(another_session_id)
                assert len(repository.sessions) == 1

    class GivenFindSession:
        """세션을 조회해야 할 때"""
        
        @pytest.fixture
        def session_id(self):
            return "test-session-123"

        @pytest.fixture
        def mock_websocket(self):
            return Mock(spec=ClientConnection)

        class WhenSessionDoesExist:
            """세션이 존재 한다면"""
            
            def then_should_return_correct_websocket(self, repository, session_id, mock_websocket):
                """올바른 웹소켓을 반환해야한다"""
                repository.create_session(session_id, mock_websocket)
                
                result = repository.find_session(session_id)
                
                assert result == mock_websocket
        
        class WhenSessionDoesNotExist:
            """세션이 존재하지 않는다면"""
            
            def then_should_raise_key_error_with_descriptive_message(self, repository, session_id):
                """KeyError를 발생시켜야한다"""
                assert not repository.is_session_exists(session_id)
                
                with pytest.raises(KeyError) as exc_info:
                    repository.find_session(session_id)

                assert f"세션 {session_id}이 연결되지 않았거나 종료됨" in str(exc_info.value)

    class GivenIsSessionExists:
        """세션 존재 여부 확인해야 할 때"""

        @pytest.fixture
        def session_id(self):
            return "test-session-123"

        @pytest.fixture
        def mock_websocket(self):
            return Mock(spec=ClientConnection)
        
        class WhenSessionDoesExist:
            """세션이 존재 한다면"""
            
            def then_should_return_true(self, repository, session_id, mock_websocket):
                """True를 반환해야한다"""
                repository.create_session(session_id, mock_websocket)
                
                result = repository.is_session_exists(session_id)
                
                assert result is True
        
        class WhenSessionDoesNotExist:
            """세션이 존재하지 않는다면"""
            
            def then_should_return_false(self, repository, session_id):
                """False를 반환해야한다"""
                assert len(repository.sessions) == 0
                
                result = repository.is_session_exists(session_id)
                
                assert result is False
        
        class WhenSessionDoesExistAndThenRemoved:
            """세션이 생성되고 제거되었다면"""
            
            def then_should_return_false(self, repository, session_id, mock_websocket):
                """False를 반환해야한다"""
                repository.create_session(session_id, mock_websocket)
                assert repository.is_session_exists(session_id)
                repository.remove_session(session_id)
                
                result = repository.is_session_exists(session_id)
                
                assert result is False