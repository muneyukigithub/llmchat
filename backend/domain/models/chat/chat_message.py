from dataclasses import dataclass
from uuid import UUID, uuid4
from domain.models.chat.chat_message_id import ChatMessageId
from domain.models.chat.chat_thread_id import ChatThreadId
from domain.models.chat.chat_message_role import Role
from domain.models.chat.chat_message_content import MessageContent

# エンティティ
class ChatMessage:
    def __init__(self,id:ChatMessageId,thread_id:ChatThreadId,role:Role,content:MessageContent):
        self._id = id
        self._thread_id = thread_id
        self._role :Role = role
        self._content = content

    @classmethod
    def create(cls,role:Role,thread_id:ChatThreadId,content:MessageContent):
        return cls(id=ChatMessageId.generate(),thread_id=thread_id,role=role,content=content)
        
    @property
    def id(self):
        return self._id

    @property
    def thread_id(self):
        return self._thread_id

    @property
    def role(self):
        return self._role

    @property
    def content(self):
        return self._content
