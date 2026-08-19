from dataclasses import dataclass
from uuid import UUID,uuid4
from domain.exceptions import InvalidValueError
from typing import ClassVar

@dataclass(frozen=True)
class ChatThreadTitle:
    value: str
    MAX_LENGTH: ClassVar[int] = 100  # ClassVar でフィールドから除外

    def __post_init__(self) -> None:
        if not  isinstance(self.value,str):
            raise InvalidValueError("Thread title must be a string.")
        
        stripped = self.value.strip()
        
        if not stripped:
            raise InvalidValueError("Thread title cannot be empty.")
        if len(stripped) > self.MAX_LENGTH:
            raise InvalidValueError("Thread title cannot exceed 100 characters.")

    def __str__(self) -> str:
        return str(self.value)