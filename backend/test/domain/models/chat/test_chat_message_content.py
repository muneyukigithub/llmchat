from mailbox import Message
from domain.models.chat.chat_message_id import ChatMessageId
from uuid import uuid4, UUID
import pytest
from domain.exceptions import InvalidValueError
from domain.models.chat.chat_message_content import MessageContent

class TestChatMessageContentInit:

  


    def test_init_message_content(self):
        content = MessageContent("Hello, world!")
        assert content.value == "Hello, world!"
        assert str(content) == "Hello, world!"

    def test_init_message_content_with_empty_string(self):
        with pytest.raises(InvalidValueError):
            MessageContent("")

    def test_init_message_content_with_none(self):
        with pytest.raises(InvalidValueError):
            MessageContent(None)

    def test_init_message_content_with_invalid_type(self):
        with pytest.raises(InvalidValueError):
            MessageContent(123)
    
    def test_quality(self):
        content1 = MessageContent("Hello, world!")
        content2 = MessageContent("Hello, world!")
        content3 = MessageContent("Hello, world!2")
        assert content1 == content2
        assert content1 != content3