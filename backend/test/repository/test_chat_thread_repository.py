import uuid
import pytest
from infrastructure.chat_thread_repository import ChatThreadRepository, RepositoryError
from domain.models.chat.chat_thread_id import ChatThreadId
from domain.models.chat.session_id import SessionId
from models.chat_threads import ChatThreadModel
from domain.models.chat.chat_message import ChatMessage
from domain.models.chat.chat_message_content import MessageContent
from domain.models.chat.chat_message_id import ChatMessageId
from domain.models.chat.chat_message_role import Role
from domain.models.chat.chat_thread import ChatThread
from domain.models.chat.chat_thread_title import ChatThreadTitle
from models.chat_messages import ChatMessageModel


class TestChatThreadRepositoryDelete:
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.db = db_session
        self.repo = ChatThreadRepository(self.db)

# 1件を削除し、DBから消えること
# 存在しないIDを渡した場合に例外が起きること

    def test_delete_one_success(self):
        thread_id_val = uuid.uuid4()
        session_id_val = uuid.uuid4()
        title_val = "新規スレッド"
        thread = ChatThreadModel(
            id=thread_id_val,
            session_id=session_id_val,
            title=title_val
        )

        self.db.add(thread)
        self.db.commit()

        self.repo.delete(ChatThreadId(thread_id_val))

        thread = self.db.get(ChatThreadModel,thread_id_val)

        assert thread is None


class TestChatThreadRepositoryFindById:

    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.db = db_session
        self.repo = ChatThreadRepository(self.db)

    def test_find_by_id_get_one_success(self):
        thread_id_val = uuid.uuid4()
        message_id_val = uuid.uuid4()
        session_id_val = uuid.uuid4()
        title_val = "新規スレッド"

        thread_model =  ChatThreadModel(
                id=thread_id_val,
                session_id=session_id_val,
                title=title_val,
            )

        message_role = "user"
        message_content =  "hello world"

        thread_message = ChatMessageModel(
            id=message_id_val,
            thread_id=thread_id_val,
            role = message_role,
            content = message_content,
        )

        self.db.add(thread_model)
        self.db.add(thread_message)
        self.db.commit()

        result = self.repo.find_by_id(ChatThreadId(thread_id_val))
        
        assert result is not None
        assert result.id == ChatThreadId(thread_id_val)
        assert result.session_id == SessionId(session_id_val)
        assert result.title == ChatThreadTitle(title_val)
        assert result.messages is not None
        messages = result.messages
        assert len(messages) == 1
        assert messages[0].id == ChatMessageId(message_id_val) 
        assert messages[0].thread_id ==ChatThreadId(thread_id_val)
        assert messages[0].role ==Role(message_role)
        assert messages[0].content ==MessageContent(message_content)

    def test_find_by_id_returns_none_when_not_found(self):
        """存在しないIDを指定した場合、Noneが返ること"""
        non_existent_id = ChatThreadId(uuid.uuid4())

        result = self.repo.find_by_id(non_existent_id)

        assert result is None

    def test_find_by_id_returns_thread_without_messages(self):
        """メッセージが存在しないスレッドを取得できること"""
        thread_id_val = uuid.uuid4()
        session_id_val = uuid.uuid4()
        title_val = "新規スレッド"

        self.db.add(
            ChatThreadModel(
                id=thread_id_val,
                session_id=session_id_val,
                title=title_val,
            )
        )
        self.db.commit()

        result = self.repo.find_by_id(ChatThreadId(thread_id_val))

        assert result is not None
        assert result.id == ChatThreadId(thread_id_val)
        assert result.session_id == SessionId(session_id_val)
        assert result.title.value == title_val
        assert result.messages == ()

class TestChatThreadRepositorySave:
    """
    save メソッドのテスト。

    【テストパターンの基本的な考え方】
    save は「新規作成（INSERT）」と「既存更新（UPDATE）」の両方を担う upsert 的なメソッドである。
    リポジトリテストでは以下の観点でパターンを分ける:

    1. 正常系の分岐網羅 — save 内の if 分岐（スレッド新規/既存、メッセージ新規/既存）を
       それぞれ独立したテストで触る。1 テストに複数分岐を詰め込まず、失敗時に原因を特定しやすくする。
    2. 永続化の確認 — 戻り値だけでなく find_by_id や DB 直接参照で「本当に保存されたか」を検証する。
       リポジトリの責務は永続化なので、副作用（DB 状態）を主たるアサーション対象とする。
    3. 契約の確認 — 戻り値 dict の shape も公開インターフェースの一部として検証する。
    4. 既存テストとの一貫性 — find_by_id テストと同様、インメモリ SQLite + db_session fixture を使い、
       テスト間の独立性（function scope）を保つ。
    """

    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.db = db_session
        self.repo = ChatThreadRepository(self.db)

    def _build_chat_thread(
        self,
        thread_id=None,
        session_id=None,
        title="新規スレッド",
        messages=None,
    ):
        thread_id = thread_id or ChatThreadId(uuid.uuid4())
        session_id = session_id or SessionId(uuid.uuid4())
        messages = messages if messages is not None else [
            ChatMessage(
                id=ChatMessageId(uuid.uuid4()),
                thread_id=thread_id,
                role=Role.USER,
                content=MessageContent("hello world"),
            )
        ]
        return ChatThread(thread_id, session_id, messages, ChatThreadTitle(title))

    def test_save_creates_new_thread_with_messages(self):
        """
        【パターン: 新規作成（INSERT）】
        根拠: save の主要パス。DB にスレッドもメッセージも存在しない状態から
        初回保存すると INSERT が発行される。最も基本的な正常系として必須。
        """
        thread_id = ChatThreadId(uuid.uuid4())
        session_id = SessionId(uuid.uuid4())
        message_id = ChatMessageId(uuid.uuid4())
        title = "新規スレッド"
        chat_thread = ChatThread(
            thread_id,
            session_id,
            [
                ChatMessage(
                    id=message_id,
                    thread_id=thread_id,
                    role=Role.USER,
                    content=MessageContent("hello world"),
                )
            ],
            ChatThreadTitle(title),
        )

        result = self.repo.save(chat_thread)

        assert result == {"thread_id": thread_id.value, "title": title}

        saved = self.repo.find_by_id(thread_id)
        assert saved is not None
        assert saved.id == thread_id
        assert saved.session_id == session_id
        assert saved.title == ChatThreadTitle(title)
        assert len(saved.messages) == 1
        assert saved.messages[0].id == message_id
        assert saved.messages[0].content == MessageContent("hello world")

    def test_save_creates_new_thread_without_messages(self):
        """
        【パターン: メッセージなしの新規作成】
        根拠: messages が空のスレッドも save 対象になりうる。
        メッセージループが 0 回でもスレッド本体は正しく INSERT されることを確認する。
        """
        thread_id = ChatThreadId(uuid.uuid4())
        session_id = SessionId(uuid.uuid4())
        title = "空のスレッド"
        chat_thread = ChatThread(thread_id, session_id, [], ChatThreadTitle(title))

        result = self.repo.save(chat_thread)

        assert result == {"thread_id": thread_id.value, "title": title}

        saved = self.repo.find_by_id(thread_id)
        assert saved is not None
        assert saved.title == ChatThreadTitle(title)
        assert saved.messages == ()

    def test_save_updates_existing_thread_fields(self):
        """
        【パターン: 既存スレッドの更新（UPDATE）】
        根拠: save は thread = self.db.get(...) で既存レコードを取得し、
        session_id / title を上書きする。2 回目の save で UPDATE 分岐が動くことを確認する。
        """
        thread_id = ChatThreadId(uuid.uuid4())
        session_id = SessionId(uuid.uuid4())
        original = self._build_chat_thread(
            thread_id=thread_id,
            session_id=session_id,
            title="旧タイトル",
        )
        self.repo.save(original)

        new_session_id = SessionId(uuid.uuid4())
        updated = ChatThread(
            thread_id,
            new_session_id,
            list(original.messages),
            ChatThreadTitle("新タイトル"),
        )
        self.repo.save(updated)

        saved = self.repo.find_by_id(thread_id)
        assert saved.session_id == new_session_id
        assert saved.title == ChatThreadTitle("新タイトル")

    def test_save_updates_existing_message_content(self):
        """
        【パターン: 既存メッセージの更新（UPDATE）】
        根拠: save 内で message = self.db.get(...) が None でない場合、
        content のみ上書きされる。ストリーミング応答の追記などで同一 ID の内容更新が起きうる。
        """
        thread_id = ChatThreadId(uuid.uuid4())
        message_id = ChatMessageId(uuid.uuid4())
        chat_thread = ChatThread(
            thread_id,
            SessionId(uuid.uuid4()),
            [
                ChatMessage(
                    id=message_id,
                    thread_id=thread_id,
                    role=Role.MODEL,
                    content=MessageContent("初期コンテンツ"),
                )
            ],
            ChatThreadTitle("スレッド"),
        )
        self.repo.save(chat_thread)

        updated_thread = ChatThread(
            thread_id,
            chat_thread.session_id,
            [
                ChatMessage(
                    id=message_id,
                    thread_id=thread_id,
                    role=Role.MODEL,
                    content=MessageContent("更新後コンテンツ"),
                )
            ],
            ChatThreadTitle("スレッド"),
        )
        self.repo.save(updated_thread)

        saved = self.repo.find_by_id(thread_id)
        assert len(saved.messages) == 1
        assert saved.messages[0].content == MessageContent("更新後コンテンツ")

    def test_save_appends_new_message_to_existing_thread(self):
        """
        【パターン: 既存スレッドへのメッセージ追加（INSERT）】
        根拠: save は messages ループ内で message is None の場合に新規 INSERT する。
        会話の進行でメッセージが増える典型フローを検証する。
        """
        thread_id = ChatThreadId(uuid.uuid4())
        first_message_id = ChatMessageId(uuid.uuid4())
        chat_thread = ChatThread(
            thread_id,
            SessionId(uuid.uuid4()),
            [
                ChatMessage(
                    id=first_message_id,
                    thread_id=thread_id,
                    role=Role.USER,
                    content=MessageContent("1通目"),
                )
            ],
            ChatThreadTitle("スレッド"),
        )
        self.repo.save(chat_thread)

        second_message_id = ChatMessageId(uuid.uuid4())
        extended_thread = ChatThread(
            thread_id,
            chat_thread.session_id,
            [
                ChatMessage(
                    id=first_message_id,
                    thread_id=thread_id,
                    role=Role.USER,
                    content=MessageContent("1通目"),
                ),
                ChatMessage(
                    id=second_message_id,
                    thread_id=thread_id,
                    role=Role.MODEL,
                    content=MessageContent("2通目"),
                ),
            ],
            ChatThreadTitle("スレッド"),
        )
        self.repo.save(extended_thread)

        saved = self.repo.find_by_id(thread_id)
        assert len(saved.messages) == 2
        assert saved.messages[0].id == first_message_id
        assert saved.messages[1].id == second_message_id
        assert saved.messages[1].content == MessageContent("2通目")

    def test_save_persists_multiple_messages_at_once(self):
        """
        【パターン: 複数メッセージの一括新規作成】
        根拠: save は for msg in chat_thread.messages でまとめて処理し、
        最後に 1 回 commit する。複数 INSERT が同一トランザクションで成功することを確認する。
        """
        thread_id = ChatThreadId(uuid.uuid4())
        message_ids = [ChatMessageId(uuid.uuid4()) for _ in range(3)]
        chat_thread = ChatThread(
            thread_id,
            SessionId(uuid.uuid4()),
            [
                ChatMessage(
                    id=message_ids[i],
                    thread_id=thread_id,
                    role=Role.USER if i % 2 == 0 else Role.MODEL,
                    content=MessageContent(f"message-{i}"),
                )
                for i in range(3)
            ],
            ChatThreadTitle("複数メッセージ"),
        )

        self.repo.save(chat_thread)

        saved = self.repo.find_by_id(thread_id)
        assert len(saved.messages) == 3
        for i, msg in enumerate(saved.messages):
            assert msg.id == message_ids[i]
            assert msg.content == MessageContent(f"message-{i}")

    

    