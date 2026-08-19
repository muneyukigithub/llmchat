import uuid
from fastapi import Depends, FastAPI, HTTPException, status,Request
from starlette.middleware.base import BaseHTTPMiddleware

class SessionCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Cookieを取得
        session_id = request.cookies.get("session_id")
        is_new_session = False

        # 2. 無ければ新規発行
        if not session_id:
            session_id = str(uuid.uuid4())
            is_new_session = True

        # 3. request.state に保存
        request.state.session_id = session_id

        # 4. エンドポイントの処理を実行（★ await は必須！）
        response = await call_next(request)

        # 5. 新規の場合のみ Cookie をセット
        if is_new_session:

            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                max_age=86400 * 7,
                samesite="lax",
            )

        return response



