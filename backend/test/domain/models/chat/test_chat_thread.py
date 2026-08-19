from concurrent.futures import thread
from email import message
import pytest
from uuid import UUID, uuid4
from unittest.mock import MagicMock
from domain.models.chat.chat_thread import ChatThread
from domain.models.chat.chat_thread_id import ChatThreadId
from domain.models.chat.session_id import SessionId
from domain.models.chat.chat_message import ChatMessage
from domain.models.chat.chat_thread_title import ChatThreadTitle
from domain.models.chat.chat_message_role import Role
from domain.exceptions import InvalidValueError, InvalidThreadOperationError

# --- ヘルパー / テスト用データ生成 ---
def create_dummy_message() -> ChatMessage:
    """テスト用のダミーChatMessageを生成するヘルパー関数"""
    msg = MagicMock(spec=ChatMessage)
    return msg

@pytest.fixture
def valid_thread_args():
    """正常なChatThread作成に必要な引数をセットアップ"""
    return {
        "chat_thread_id": MagicMock(spec=ChatThreadId),
        "session_id": MagicMock(spec=SessionId),
        "messages": [create_dummy_message()],
        "title": MagicMock(spec=ChatThreadTitle),
    }

def create_dummy_thread():
    thread_id = uuid4()
    session_id = uuid4()
    messages = []
    title = ""
    thread = ChatThread(thread_id,session_id,messages,title)
    return thread


# --- テストクラス ---
class TestChatThreadInit:
    """初期化 (__init__) のテスト"""

    def test_init_success_with_valid_messages(self, valid_thread_args):
        # 100件以下のメッセージで正常生成できること
        thread = ChatThread(**valid_thread_args)
        assert len(thread.messages) == 1

    def test_init_raises_error_when_messages_exceed_limit(self, valid_thread_args):
        # 101件のメッセージを渡すと InvalidValueError が発生すること
        valid_thread_args["messages"] = [create_dummy_message() for _ in range(101)]
        
        with pytest.raises(InvalidValueError) as excinfo:
            ChatThread(**valid_thread_args)
        assert "100件がメッセージ上限" in str(excinfo.value)

    def test_create_value(self):
        session_id = uuid4()
        thread = ChatThread.create(session_id)

        assert thread.title.value == "新しいチャット"
        assert thread.messages[0].content.value == "メッセージを入力してください"
        assert len(thread.messages) == 1
    
class TestAddMessage:
    
    def test_add_message_success(self):
        message = create_dummy_message()
        session_id = uuid4()
        thread = ChatThread.create(session_id)
        thread.add_message(message)

        assert len(thread.messages) == 2

    def test_add_message_99_to_100(self):
        # 境界値テスト
        message = create_dummy_message()
        thread = create_dummy_thread()

        for _ in range(99):
            thread.add_message(message)
        
        thread.add_message(message)

        assert len(thread.messages) == 100

    def test_add_message_100_to_101(self):
        # 境界値テスト
        message = create_dummy_message()
        thread = create_dummy_thread()

        for _ in range(100):
            thread.add_message(message)
        
        with pytest.raises(InvalidThreadOperationError):
            thread.add_message(create_dummy_message())

class TestThreadChangeTitle:

    def test_change_title(self):
        thread = create_dummy_thread()
        thread.change_title("new title")

        assert thread.title.value == "new title"

class TestChatThreadEncapsulation:

    def test_messages_property_is_immutable(self,valid_thread_args):
        thread = ChatThread(**valid_thread_args)
        message = create_dummy_message()

        with pytest.raises(AttributeError):
            thread.messages.append(message)

