from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# スレッド一覧画面用の DTO（メッセージ件数や最新更新日時だけを持つ）
class ChatThreadSummaryDTO(BaseModel):
    chat_id: UUID
    title: str
    updated_at: datetime

# スレッド詳細画面用の DTO（画面表示用にネストさせた構造）
class ChatMessageDTO(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

class ChatThreadDetailDTO(BaseModel):
    chat_id: UUID
    title: str
    messages: List