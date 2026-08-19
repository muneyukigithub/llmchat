from abc import ABC, abstractmethod
from typing import Optional
from domain.models.chat.chat_thread_id import ChatThreadId

class IChatThreadRepository(ABC):
    
    @abstractmethod
    def save(self,chat_thread_id:ChatThreadId):
        pass

    @abstractmethod
    def find_by_id(self,chat_thread_id:ChatThreadId):
        pass

    @abstractmethod
    def delete(self, chat_thread_id: ChatThreadId) -> None:
        pass