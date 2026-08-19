import os
from enum import Enum
import time
from google import genai
from google.genai import types
from typing import Any, AsyncIterator, Callable
from domain.models.chat.chat_message_role import Role



class GeminiModel(str, Enum):
    """利用可能なGeminiモデルの定義。

    モデルの追加・変更が発生した場合は本Enumのみを更新します。
    """

    FLASH = "gemini-3-flash-preview"
    PRO = "gemini-3.1-pro-preview"
    FLASH_LITE = "gemini-3.1-flash-lite"


class GeminiService:

    def __init__(self,gemini_client, model_name: str = GeminiModel.FLASH_LITE.value) -> None:
        # api_key = os.getenv("GEMINI_API_KEY")
        # if not api_key:
        #     raise ValueError("api_keyが設定されていません")

        # if GeminiService._gemini_client is None:
        #     GeminiService._gemini_client = genai.Client(api_key=api_key)
        self.client = gemini_client
        self.model_name = model_name

    def get_history(self):
        return GeminiService._gemini_client.get_history()

    def _tool_map(self, config: types.GenerateContentConfig | None) -> dict[str, Callable]:
        """config.tools から name -> callable の辞書を作る。"""
        if not config or not config.tools:
            return {}
        mapping: dict[str, Callable] = {}
        for tool in config.tools:
            if callable(tool):
                mapping[tool.__name__] = tool
        return mapping

    def _build_function_response_parts(
        self,
        function_calls: list,
        tool_map: dict[str, Callable],
    ) -> list[types.Part]:
        """function_call を実行し、FunctionResponse Part のリストを返す。"""
        parts: list[types.Part] = []
        for call in function_calls:
            func = tool_map.get(call.name)
            if func is None:
                result = f"未知の関数です: {call.name}"
            else:
                try:
                    args = dict(call.args) if call.args else {}
                    result = func(**args)
                except Exception as e:
                    result = f"関数実行エラー: {e}"

            # print(f"★ 手動ツール実行: {call.name}({call.args}) -> {str(result)[:200]}")
            parts.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={"result": result},
                )
            )
        return parts

    async def chat_invoke(self,prompt:str,messages=[],system_instruction = None,temperature=2.0,tools=[]):

        context = [
            types.Content(
                role=message.role.value,
                parts=[types.Part.from_text(text=message.content.value)],
            )
            for message in messages
        ]

        user_prompt = types.Content(
            role=Role.USER.value,
            parts=[types.Part.from_text(text=prompt)],
        )

        contents = context + [user_prompt]

        response =await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=contents,
            config= types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            tools=tools,
        ))

        return response.text


    async def stream_chat_async(
        self,
        prompt: Any,
        config: types.GenerateContentConfig | None = None,
    ) -> AsyncIterator[str]:
        """Gemini APIからのレスポンスを非同期で返す。

        AFC 無効時は function_call を検出し、手動実行→再生成する。
        """
        tool_map = self._tool_map(config)
        contents = prompt
        max_tool_rounds = 5

        for _ in range(max_tool_rounds):
            response = await GeminiService._gemini_client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            # テキスト回答があればそのまま返す
            if response.text:
                yield response.text

            # function_call があれば手動実行して会話に戻す
            if response.function_calls and tool_map:
                model_content = response.candidates[0].content
                fr_parts = self._build_function_response_parts(
                    response.function_calls, tool_map
                )
                function_response_content = types.Content(
                    role="user",
                    parts=fr_parts,
                )

                # 履歴が list の場合はそのまま追記、文字列の場合は組み立て直す
                if isinstance(contents, list):
                    contents = contents + [model_content, function_response_content]
                else:
                    contents = [
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=str(contents))],
                        ),
                        model_content,
                        function_response_content,
                    ]
                continue

            # テキストも function_call も無い場合は終了
            return

        yield "ツール呼び出しの上限に達しました。もう一度お試しください。"

    # ------------------------------------------------------------------
    # ファクトリメソッド（呼び出し側の記述簡略化およびモデル切り替えの抽象化）
    # ------------------------------------------------------------------
    @classmethod
    def flash(cls) -> "GeminiService":
        """標準（Flash）モデルのインスタンスを生成して返します。"""
        return cls(model_name=GeminiModel.FLASH.value)

    @classmethod
    def pro(cls) -> "GeminiService":
        """高精度（Pro）モデルのインスタンスを生成して返します。"""
        return cls(model_name=GeminiModel.PRO.value)

    @classmethod
    def flash_lite(cls) -> "GeminiService":
        """軽量（Flash-Lite）モデルのインスタンスを生成して返します。"""
        return cls(model_name=GeminiModel.FLASH_LITE.value)
