from dataclasses import dataclass
from uuid import UUID,uuid4
from typing import List
from domain.models.chat.chat_thread_id import ChatThreadId
from domain.models.chat.session_id import SessionId
from domain.models.chat.chat_message import ChatMessage
from domain.models.chat.chat_thread_title import ChatThreadTitle
from domain.models.chat.chat_message_content import MessageContent
from domain.models.chat.chat_message_role import Role
from domain.exceptions import InvalidValueError,InvalidThreadOperationError

class ChatThread:
    MAX_MESSAGES_LIMIT : int = 100

    def __init__(self,chat_thread_id,session_id,messages:list,title:str):
        if len(messages) > 100:
            raise InvalidValueError("100件がメッセージ上限")

        self._id :ChatThreadId = chat_thread_id
        self._session_id :SessionId= session_id
        self._messages:List[ChatMessage] = messages
        self._title :ChatThreadTitle= title

    @classmethod
    def create(cls,session_id:UUID):
        id = ChatThreadId.generate()
        welcam_text = "メッセージを入力してください"
        title="新しいチャット"
        chat_message = ChatMessage.create(Role.MODEL,id,MessageContent(value=welcam_text))
        return cls(id,SessionId(session_id),[chat_message],ChatThreadTitle(title))
    
    @classmethod
    def reconstruct(cls,id:ChatThreadId,session_id,messages:List[ChatMessage],title):
        pass

    # 事後条件(正常パターン)：引数で渡したメッセージがスレッドに追加されていること
    # 確認①メソッド呼び出し後にメッセージリストの数が1増えていること
    # 確認②：メソッド呼び出し後にメッセージリストに同じプロパティを持ったメッセージが追加されること
    
    #　異常系：MAX_MESSAGES_LIMITを超えた場合に例外
    #　理由：事前条件が満たされないから異常系に分類
    def add_message(self,message:ChatMessage):
        if len(self._messages) >= self.MAX_MESSAGES_LIMIT:
            raise InvalidThreadOperationError("")

        self._messages.append(message)
        # self.updated_at = datetime.now(timezone.utc)

    # 事後条件(正常パターン)：スレッドタイトルが引数で渡したタイトルに変更されること
    # 確認メソッド呼び出し後にタイトルの変更を確認する
    
    #　異常系：変更タイトルが文字以外の数字、真偽などを渡す
    #　理由：文字以外のタイトルを受け取るとその時点で例外、事後条件が満たされないため
    def change_title(self,new_title:str):
        self._title = ChatThreadTitle(new_title)

    @property
    def id(self):
        return self._id

    @property
    def session_id(self):
        return self._session_id

    @property
    def title(self):
        return self._title

    @property
    def messages(self): 
        return tuple(self._messages)