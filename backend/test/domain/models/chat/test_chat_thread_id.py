from domain.models.chat.chat_thread_id import ChatThreadId
from uuid import uuid4
from domain.exceptions import InvalidValueError
import pytest
from dataclasses import FrozenInstanceError

class TestChatThreadIdInit:
    def test_init_chat_thread_id(self):
        uuid = uuid4()
        thread_id = ChatThreadId(uuid)
        assert thread_id.value == uuid
        assert str(thread_id) == str(uuid)
        assert isinstance(thread_id, ChatThreadId)
    
    def test_init_chat_thread_id_with_invalid_value(self):
        with pytest.raises(InvalidValueError):
            ChatThreadId("invalid_value")
    
    def test_generate(self):
        thread_id = ChatThreadId.generate()
        assert isinstance(thread_id,ChatThreadId)

    def test_chat_thread_id_replace_with_valid_value(self):
        thread_id = ChatThreadId(uuid4())
        with pytest.raises(FrozenInstanceError):
            thread_id.value = uuid4()

    def test_quality(self):
        uuid = uuid4()
        thread_id1 = ChatThreadId(uuid)
        thread_id2 = ChatThreadId(uuid)
        thread_id3 = ChatThreadId(uuid4())
        assert thread_id1 == thread_id2
        assert thread_id1 != thread_id3