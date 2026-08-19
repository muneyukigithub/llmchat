from dataclasses import dataclass
from uuid import UUID,uuid4
from domain.exceptions import InvalidValueError

@dataclass(frozen=True)
class ChatThreadId:
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value,UUID):
            raise InvalidValueError("")

    @classmethod
    def generate(cls):
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)
