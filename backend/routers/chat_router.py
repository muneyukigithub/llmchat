from contextlib import asynccontextmanager
import os
import asyncio
from typing import AsyncIterator,List
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, status,Request,APIRouter
from fastapi.responses import StreamingResponse
from google.genai import types
from pydantic import BaseModel, Field
from psycopg2.extras import Json
from infrastructure.queries.chat_thread_query import ChatThreadQuery
from application.chat.dtos.chat_thread_dto import ChatThreadSummaryDTO,ChatMessageDTO
from application.chat.commands.chat_application_service import ChatApplicationService
from domain.exceptions import (
    InvalidValueError,
    ThreadNotFoundError,
    SessionMismatchError,
)
from routers.dependencies import get_chat_application_service, get_chat_query

# ------------------------------------------------------------------
# 1. リクエスト / レスポンスのスキーマ定義 (Pydantic)
# ------------------------------------------------------------------
class ChatRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        description="送信するプロンプト文字列（空文字不可）",
        examples=["PythonのFastAPIについて簡潔に説明してください。"],
    )
    thread_id: str = Field(
        ...,
        min_length=1,
        description="対象チャットスレッドID",
    )
    system_instruction: str | None = Field(
        default=None,
        description="オプションのシステムプロンプト",
        examples=["あなたは優秀なソフトウェアエンジニアです。"],
    )
    temperature: float | None = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="生成の多様性パラメータ（0.0〜2.0）",
    )

class MessageRequest(BaseModel):
    thread_id:str = Field(
        ...,
        min_lenght=1,
        description="対象チャットスレッドID"
    )

class RenameThreadRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="新しいスレッドタイトル",
    )


# セッションIDを依存注入で取得する関数
def get_session_id(request: Request) -> UUID:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Session ID missing in cookies"
        )
    return UUID(session_id)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.get("/threads",response_model=List[ChatThreadSummaryDTO])
def get_chat_threads(
        session_id:UUID = Depends(get_session_id),
        chat_query:ChatThreadQuery= Depends(get_chat_query)):
    
    threads = chat_query.get_chat_threads(session_id)
    return threads
    
@router.post("/messages",summary="1つのスレッドのメッセージ一覧取得",response_model=List[ChatMessageDTO])
def get_chat_messages(request:MessageRequest,
        chat_query:ChatThreadQuery= Depends(get_chat_query)):
    
    chat_thread_id = request.thread_id
    result = chat_query.get_chat_thread_messages(chat_thread_id)
    return result

@router.post("/create", summary="チャット新規作成")
def chat_create(
    session_id: UUID = Depends(get_session_id),
    app_service:ChatApplicationService = Depends(get_chat_application_service)):
    return app_service.create_chat(session_id=session_id)


@router.patch("/threads/{thread_id}/title", summary="チャットタイトル変更")
def rename_chat_thread(
    thread_id: UUID,
    request: RenameThreadRequest,
    session_id: UUID = Depends(get_session_id),
    app_service: ChatApplicationService = Depends(get_chat_application_service),
):
    try:
        return app_service.rename_chat(
            thread_id=thread_id,
            session_id=session_id,
            title=request.title,
        )
    except ThreadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except SessionMismatchError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except InvalidValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/threads/{thread_id}", summary="チャット削除")
def delete_chat_thread(
    thread_id: UUID,
    session_id: UUID = Depends(get_session_id),
    app_service: ChatApplicationService = Depends(get_chat_application_service),
):
    try:
        return app_service.delete_chat(thread_id=thread_id, session_id=session_id)
    except ThreadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except SessionMismatchError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


@router.post("/",summary="LLMに質問する")
async def chat(
    request: ChatRequest,
    session_id: str = Depends(get_session_id),
    app_service:ChatApplicationService = Depends(get_chat_application_service),
    ):

    thread_id = UUID(request.thread_id)
    prompt = request.prompt

    return await app_service.chat(
        thread_id=thread_id,
        session_id=session_id,
        prompt=prompt
    )


# @router.post("/",summary="LLMに質問する")
# async def chat(
#     request: ChatRequest,
#     session_id: str = Depends(get_session_id),
#     conn=Depends(get_db),
#     geminiService: GeminiService = Depends(get_gemini_service),
# ):
#     cur = conn.cursor()
#     chat_thread_id = request.thread_id
#     prompt = request.prompt

#     try:
#         # スレッドがこのセッションのものか確認
#         cur.execute(
#             """
#             SELECT 1 FROM chat_threads
#             WHERE chat_id = %s AND session_id = %s
#             """,
#             (chat_thread_id, session_id),
#         )
#         if cur.fetchone() is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="指定されたチャットスレッドが見つかりません",
#             )

#         # 古い順で履歴を取得（Gemini に渡す文脈用）
#         cur.execute(
#             """
#             SELECT role, content
#                 FROM (
#                     SELECT id, role, content, created_at
#                     FROM chat_messages
#                     WHERE chat_id = %s
#                     ORDER BY created_at DESC, id DESC
#                     LIMIT 10
#                 ) AS recent_messages
#                 ORDER BY created_at ASC, id ASC;
#             """,
#             (chat_thread_id,),
#         )
#         rows = cur.fetchall()

#         context = [
#             types.Content(
#                 role=row[0],
#                 parts=[types.Part.from_text(text=row[1])],
#             )
#             for row in rows
#         ]

#         user_prompt = types.Content(
#             role="user",
#             parts=[types.Part.from_text(text=prompt)],
#         )
#         contents = context + [user_prompt]

#         config = types.GenerateContentConfig(
#             system_instruction=request.system_instruction,
#             temperature=request.temperature,
#             tools=[search_web],
#         )

#         response_text = await geminiService.chat_invoke(
#             contents=contents, config=config
#         )
#         if not response_text:
#             response_text = ""

#         cur.execute(
#             """
#             INSERT INTO chat_messages (chat_id, role, content)
#             VALUES (%s, %s, %s)
#             """,
#             (chat_thread_id, "user", prompt),
#         )
#         cur.execute(
#             """
#             INSERT INTO chat_messages (chat_id, role, content)
#             VALUES (%s, %s, %s)
#             """,
#             (chat_thread_id, "model", response_text),
#         )
#         cur.execute(
#             """
#             UPDATE chat_threads
#             SET updated_at = CURRENT_TIMESTAMP
#             WHERE chat_id = %s
#             """,
#             (chat_thread_id,),
#         )
#         conn.commit()

#         return {"value": response_text}

#     except HTTPException:
#         conn.rollback()
#         raise
#     except Exception as e:
#         print(e)
#         conn.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"チャット処理に失敗しました: {e}",
#         ) from e
#     finally:
#         cur.close()


# @router.post(
#     "/api/v1/chat/stream",
#     summary="ストリーミングチャット応答の取得",
#     description="プロンプトを受け取り、プレーンテキスト形式でレスポンスをリアルタイム配信します。",
# )
# async def chat_stream(
#     request: ChatRequest,
#     service: GeminiService = Depends(get_gemini_service),
#     conn = Depends(get_db),
#     session_id = Depends(get_session_id)
    
# ):


#     # tool_config は「モデルが関数を呼ぶかどうか」の制御（AUTO/ANY/NONE）
#     # AFC（SDKが関数を自動実行すること）の無効化は automatic_function_calling で行う
#     config = types.GenerateContentConfig(
#         system_instruction=request.system_instruction,
#         temperature=request.temperature,
#         tools=[search_web],
#         automatic_function_calling=types.AutomaticFunctionCallingConfig(
#             disable=True
#         ),
#     )

#     return StreamingResponse(
#         plain_text_stream_generator(
#             session_id,conn,service=service, 
#             prompt=request.prompt, 
#             config=config
#         ),
#         media_type="text/plain",  # SSE ではなくプレーンテキストとしてレスポンス
#         headers={
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive",
#             "X-Accel-Buffering": "no",  # Nginx等のリバースプロキシでのバッファリングを防止
#         },
#     )
   
# async def plain_text_stream_generator(
#     session_id,conn,service: GeminiService, prompt: str, config: types.GenerateContentConfig
# ) -> AsyncIterator[str]:

#     cur = conn.cursor()
#     try:
#         # 1. DBから既存の会話履歴を取得
#         cur.execute(
#             "SELECT history FROM chat_sessions WHERE session_id = %s;",
#             (session_id,)
#         )
#         row = cur.fetchone()
#         raw_history = row[0] if row else []

#         # 2. 既存履歴を Content オブジェクトに復元
#         typed_history = [types.Content(**item) for item in raw_history]

#         # 3. 今回のユーザープロンプトを Content オブジェクトとして追加 (不備1の修正)
#         user_content = types.Content(
#             role="user",
#             parts=[types.Part.from_text(text=prompt)]
#         )
#         full_history = typed_history + [user_content]

#         # 4. ストリーミング送信＆AIの返答テキストを蓄積
#         ai_response_text = ""
#         async for chunk in service.stream_chat_async(full_history, config=config):
#             ai_response_text += chunk
#             yield chunk

#         # 5. AIの回答を Content オブジェクトにして履歴に追加 (不備2の修正)
#         model_content = types.Content(
#             role="model",
#             parts=[types.Part.from_text(text=ai_response_text)]
#         )
#         updated_typed_history = full_history + [model_content]

#         # 6. JSONB保存用に model_dump() で辞書化
#         updated_history_dict = [content.model_dump() for content in updated_typed_history]

#         # 7. DBへ保存
#         cur.execute("""
#             INSERT INTO chat_sessions (session_id, user_id, history, updated_at)
#             VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
#             ON CONFLICT (session_id) 
#             DO UPDATE SET 
#                 history = EXCLUDED.history,
#                 updated_at = CURRENT_TIMESTAMP;
#         """, (session_id, "user_default", Json(updated_history_dict)))
        
#         conn.commit()

#     except Exception as e:
#         conn.rollback()
#         raise e
#     finally:
#         # エラーが起きても確実にカーソルを閉じる (不備4の修正)
#         cur.close()

@router.get("/health", summary="ヘルスチェックエンドポイント")
async def health_check():
    return {"status": "ok"}