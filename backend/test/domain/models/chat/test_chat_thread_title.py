from domain.models.chat.chat_thread_id import ChatThreadId
from uuid import uuid4
from domain.exceptions import InvalidValueError
import pytest
from dataclasses import FrozenInstanceError
from domain.models.chat.chat_thread_title import ChatThreadTitle

class TestChatThreadTitleInit:
    def test_init_chat_thread_title(self):
        title = "Hello, world!"
        thread_title = ChatThreadTitle(title)
        assert thread_title.value == title
        assert str(thread_title) == title

    def test_init_chat_thread_title_raises_empty(self):
        title = ""
        with pytest.raises(InvalidValueError):
            thread_title = ChatThreadTitle(title)

    def test_init_chat_thread_title_raises_max_length(self):
        title = "a" * 100
        thread_title = ChatThreadTitle(title)          
        assert thread_title.value == title

    def test_init_chat_thread_title_raises_exceeds_limit(self):
        title = "a" * 101
        with pytest.raises(InvalidValueError):
            thread_title = ChatThreadTitle(title)

    def test_init_chat_thread_title_raises_invalid_value(self):
        title = 123
        with pytest.raises(InvalidValueError):
            thread_title = ChatThreadTitle(title)

    def test_immutable(self):
        title = "Hello, world!"
        thread_title = ChatThreadTitle(title)
        with pytest.raises(FrozenInstanceError):
            thread_title.value = "a"

    def test_equality(self):
        # 同じ値を持つVO同士が等価と判定されるか
        title1 = ChatThreadTitle("Hello")
        title2 = ChatThreadTitle("Hello")
        title3 = ChatThreadTitle("World")

        assert title1 == title2
        assert title1 != title3