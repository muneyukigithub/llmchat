from contextlib import asynccontextmanager
import os
from fastapi import Depends, FastAPI, HTTPException, status,Request
from fastapi.middleware.cors import CORSMiddleware
from middleware import SessionCookieMiddleware
from dotenv import load_dotenv
from routers.chat_router import router

# .env ファイルの内容を読み込む
load_dotenv()

# ------------------------------------------------------------------
# アプリケーションのライフサイクル管理 (Fail-Fast)
# ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーション起動時に必須環境変数を検証します。"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "環境変数 'GEMINI_API_KEY' が設定されていません。サーバーを起動できません。"
        )

    
    yield


app = FastAPI(
    title="Gemini API Service",
    description="google-genai SDKを使用したプロダクション向けチャットAPI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(SessionCookieMiddleware)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # すべてのドメインからのアクセスを許可（開発用）
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # OPTIONS や POST などすべてのメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# ルーターを組み込む
app.include_router(router)