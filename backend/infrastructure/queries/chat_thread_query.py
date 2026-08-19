from concurrent.futures import thread
from core.database import get_db
from typing import Optional, Dict, Any,List
from application.chat.dtos.chat_thread_dto import ChatThreadSummaryDTO,ChatMessageDTO
from sqlalchemy import select
from models.chat_threads import ChatThreadModel
from models.chat_messages import ChatMessageModel
class ChatThreadQuery:

    def __init__(self,db):
        self.db = db

    def get_chat_threads(self, session_id: str):
        stmt = (
            select(
                ChatThreadModel.id,
                ChatThreadModel.title,
                ChatThreadModel.updated_at
            )
            .where(ChatThreadModel.session_id == str(session_id))
            .order_by(ChatThreadModel.updated_at.desc())
        )
        
        rows = self.db.execute(stmt).all()
        
        return [
            ChatThreadSummaryDTO(
                chat_id=row.id,
                title=row.title,
                updated_at=row.updated_at
            )
            for row in rows
        ]

    def get_chat_thread_messages(self,thread_id:str):

        stmt = (
            select(
                ChatMessageModel.id,
                ChatMessageModel.role,
                ChatMessageModel.content,
                ChatMessageModel.created_at
            )
            .where(ChatMessageModel.thread_id == thread_id)
            .order_by(ChatMessageModel.created_at.asc())
        )

        rows = self.db.execute(stmt).all()

        
        return [
            ChatMessageDTO(
                id=row[0],
                role=row[1],
                content=row[2],
                created_at=row[3]
            ) for row in rows
        ]
