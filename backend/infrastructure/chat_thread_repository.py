from fastapi import Depends, FastAPI, HTTPException, status,Request,APIRouter
from typing import Optional, Dict, Any,List
from domain.models.chat.chat_thread import ChatThread
from domain.models.chat.chat_thread_id import ChatThreadId
from domain.models.chat.chat_thread_title import ChatThreadTitle
from domain.models.chat.session_id import SessionId
from domain.models.chat.chat_message import ChatMessage
from domain.models.chat.chat_message_content import MessageContent
from domain.models.chat.chat_message_role import Role
from domain.models.chat.chat_message_id import ChatMessageId
from domain.repositories.chat_thread_repository_interface import IChatThreadRepository
from models.chat_threads import ChatThreadModel
from models.chat_messages import ChatMessageModel

# ドメイン/リポジトリ層の例外定義（任意）
class RepositoryError(Exception):
    """リポジトリ層での基本例外"""
    pass

class ChatThreadRepository(IChatThreadRepository):

    def __init__(self, db):
        self.db = db

    def save(self, chat_thread: ChatThread) -> dict:
        try:
            thread_id_str = chat_thread.id.value

            # 1. 既存スレッドの検索（無ければ新規作成してセッションに追加）
            thread = self.db.get(ChatThreadModel, thread_id_str)
            if thread is None:
                thread = ChatThreadModel(id=thread_id_str)
                self.db.add(thread)

            # 値の更新（変更があればコミット時に自動で UPDATE が発行される）
            thread.session_id = chat_thread.session_id.value
            thread.title = chat_thread.title.value

            # 2. メッセージの更新・追加
            for msg in chat_thread.messages:
                msg_id_str = msg.id.value
                message = self.db.get(ChatMessageModel, msg_id_str)

                if message is None:
                    message = ChatMessageModel(
                        id=msg_id_str,
                        thread_id=thread_id_str,
                        role=msg.role.value,
                    )
                    self.db.add(message)

                message.content = msg.content.value

            # 3. まとめコミット（変更検知により必要な INSERT / UPDATE が一括実行される）
            self.db.commit()

            return {
                "thread_id": chat_thread.id.value,
                "title": chat_thread.title.value,
            }

        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"チャットスレッドの作成に失敗しました: {e}") from e

    def find_by_id(self, chat_thread_id: ChatThreadId) -> Optional[ChatThread]:
        thread = self.db.get(ChatThreadModel, chat_thread_id.value)
        if thread is None:
            return None

        thread_id = ChatThreadId(thread.id)
        session_id = SessionId(thread.session_id)
        title = ChatThreadTitle(thread.title)

        messages: List[ChatMessage] = []
        for msg in sorted(thread.messages, key=lambda m: m.created_at):
            messages.append(
                ChatMessage(
                    id=ChatMessageId(msg.id),
                    thread_id=thread_id,
                    role=Role(msg.role),
                    content=MessageContent(msg.content),
                )
            )

        return ChatThread(
            chat_thread_id=thread_id,
            session_id=session_id,
            messages=messages,
            title=title,
        )

    def delete(self, chat_thread_id: ChatThreadId) -> None:
        try:
            thread = self.db.get(ChatThreadModel, chat_thread_id.value)
            if thread is not None:
                self.db.delete(thread)
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"チャットスレッドの削除に失敗しました: {e}") from e
