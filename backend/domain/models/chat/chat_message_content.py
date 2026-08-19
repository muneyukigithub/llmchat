from dataclasses import dataclass
from uuid import UUID,uuid4
from domain.exceptions import InvalidValueError

@dataclass(frozen=True)
class MessageContent:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or len(self.value.strip()) == 0:
            raise InvalidValueError("Message content cannot be empty.")

    def __str__(self) -> str:
        return self.value