from dataclasses import dataclass
from uuid import UUID,uuid4
from domain.exceptions import InvalidValueError

@dataclass(frozen=True)
class SessionId:
    value : UUID

    def __post_init__(self):
        if not isinstance(self.value,UUID):
            raise InvalidValueError("")