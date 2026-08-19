from domain.models.chat.chat_message import ChatMessage
from domain.models.chat.chat_message_id import ChatMessageId
from domain.models.chat.chat_message_content import MessageContent
from domain.models.chat.chat_message_role import Role
from domain.models.chat.chat_thread_id import ChatThreadId
from datetime import datetime
from uuid import uuid4
class TestChatMessageInit:
    def setup_method(self):
        self.message = ChatMessage(
            id=ChatMessageId(uuid4()),
            content=MessageContent("Hello, world!"),
            role=Role.USER,
            thread_id=ChatThreadId(uuid4()),
        )

    def test_chat_message_init(self):
        message = self.message
        assert message.content == MessageContent("Hello, world!")
        assert message.role == Role.USER
        assert isinstance(message.id, ChatMessageId)
        assert isinstance(message.thread_id, ChatThreadId)

class TestChatMessageCreate:
    def setup_method(self):
        self.message = ChatMessage.create(
            content=MessageContent("Hello, world!"),
            role=Role.USER,
            thread_id=ChatThreadId(uuid4()),
        )

    def test_chat_message_create(self):
        message = self.message
        assert message.content == MessageContent("Hello, world!")
        assert message.role == Role.USER
        assert isinstance(message.id, ChatMessageId)
        assert isinstance(message.thread_id, ChatThreadId)