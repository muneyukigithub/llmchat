import pytest
from infrastructure.chat_thread_repository import ChatThreadRepository
from application.chat.commands.chat_application_service import ChatApplicationService 
from unittest.mock import MagicMock, AsyncMock
import uuid
from domain.exceptions import InvalidValueError,SessionMismatchError

from domain.models.chat import session_id
from domain.models.chat.chat_thread import ChatThread
from domain.models.chat.chat_thread_id import ChatThreadId

class TestChatThreadApplication:

    @pytest.fixture(autouse=True)
    def setup(self):

        mock_repo = MagicMock()
        mock_repo.save = MagicMock()

        mock_llm_service = MagicMock()
        mock_llm_service.chat_invoke = AsyncMock(return_value="モックされたLLMの回答です")
    
        mock_search_web_service = MagicMock()
        mock_search_web_service.search_web = MagicMock()

        self.mock_repo = mock_repo
        self.mock_llm_service = mock_llm_service
        self.app = ChatApplicationService(mock_repo,mock_llm_service,mock_search_web_service)

    def test_chatApplication_create_chat_success(self):
        session_id = uuid.uuid4()
        self.app.create_chat(session_id)
        self.mock_repo.save.assert_called_once()

    
    def test_chatApplication_rename_chat_success(self):
        thread_id = uuid.uuid4()
        session_id = uuid.uuid4()
        title = "変更"

        thread = MagicMock()
        thread.session_id.value = session_id

        self.mock_repo.find_by_id.return_value = thread
        
        self.app.rename_chat(thread_id,session_id,title)

        self.mock_repo.find_by_id.assert_called_once_with(ChatThreadId(thread_id))
        thread.change_title.assert_called_once_with(title)
        self.mock_repo.save.assert_called_once_with(thread)


    # 正常系
    # 事後条件：渡されたメッセージIDでdeleteメソッドを呼ぶ
    # 確認①：deleteメソッドが1回呼ばれていること
    # 確認②：deleteメソッドの引数が渡されたメッセージIDと一致すること
    def test_chatApplication_delete_chat_success(self):
        # 準備
        thread_id = uuid.uuid4()
        session_id = uuid.uuid4()
        thread = MagicMock()
        thread_id_obj = MagicMock()
        thread.id = thread_id_obj
        thread.session_id.value = session_id
        self.mock_repo.find_by_id.return_value = thread
        
        # 実行
        self.app.delete_chat(thread_id,session_id)

        # 確認
        self.mock_repo.delete.assert_called_once_with(thread_id_obj)

     
    # 異常系：session_idがスレッドのsession_idと一致しない
    # 理由：session_idの一致の事前条件違反
    # 確認①：例外が発生すること
    def test_chatApplication_delete_chat_thread_id_empty(self):
        # 準備
        thread_id_value = uuid.uuid4()
        session_id_value = uuid.uuid4()
        thread = MagicMock()
        thread_id = MagicMock()
        thread.id = thread_id
        thread.session_id.value = uuid.uuid4()
        self.mock_repo.find_by_id.return_value = thread
        
        # 実行 確認
        with pytest.raises(SessionMismatchError):
            self.app.delete_chat(thread_id_value,session_id_value)


    @pytest.mark.asyncio
    async def test_chat_success(self):

        # リポジトリが正常なスレッドを返すように設定
        fake_thread = MagicMock()
        fake_thread.id.value = uuid.uuid4()
        fake_thread.session_id.value = uuid.uuid4()
        self.mock_repo.find_by_id.return_value = fake_thread

        # 3. テスト対象（async メソッド）の実行
        result = await self.app.chat(
            thread_id=fake_thread.id.value,
            session_id=fake_thread.session_id.value,
            prompt="こんにちは"
        )

        # ① AsyncMock が1回 await 呼び出しされたこと
        self.mock_llm_service.chat_invoke.assert_awaited_once()

        # ③ 戻り値の確認
        assert result == {"value": "モックされたLLMの回答です"}