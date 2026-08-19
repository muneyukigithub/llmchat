from dataclasses import dataclass
from uuid import UUID,uuid4
from domain.exceptions import InvalidValueError
from enum import Enum

# 値オブジェクト
class Role(Enum):
    USER = "user"
    MODEL = "model"