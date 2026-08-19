from dataclasses import dataclass
from uuid import UUID,uuid4
from domain.exceptions import InvalidValueError

# 値オブジェクト
@dataclass(frozen=True)
class ChatMessageId:
    value : UUID

    def __post_init__(self):
        if isinstance(self.value, str):
            try:
                object.__setattr__(self, 'value', UUID(self.value))
            except ValueError:
                raise InvalidValueError("ChatMessageId は有効な UUID である必要があります。")

        if not isinstance(self.value,UUID):
            raise InvalidValueError("ChatMessageId must be a UUID")

    @classmethod
    def generate(cls):
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)