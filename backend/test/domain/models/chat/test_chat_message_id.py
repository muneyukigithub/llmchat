from domain.models.chat.chat_message_id import ChatMessageId
from uuid import uuid4, UUID
import pytest
from domain.exceptions import InvalidValueError

class TestChatMessageIdInit:
    def test_init_with_uuid(self):
        uuid = uuid4()
        message_id = ChatMessageId(uuid)
        assert message_id.value == uuid

    def test_init_with_valid_uuid_string(self):
        uuid_str = "12345678-1234-5678-1234-567812345678"
        message_id = ChatMessageId(uuid_str)
        assert message_id.value == UUID(uuid_str)

    def test_equality(self):
        uuid = uuid4()
        message_id1 = ChatMessageId(uuid)
        message_id2 = ChatMessageId(uuid)
        message_id3 = ChatMessageId.generate()
        assert message_id1 == message_id2
        assert message_id1 != message_id3
        assert message_id2 != message_id3

    def test_chat_message_id_init(self):
        message_id = ChatMessageId(uuid4())
        assert isinstance(message_id,ChatMessageId)

    def test_chat_message_id_raise_invalid_value_error(self):
        with pytest.raises(InvalidValueError):
            ChatMessageId("invalid_value")