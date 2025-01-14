from enum import Enum

class StatusEnum(int, Enum):
    DAMAGED = 1
    UNDER_ATTACK = 2
    FUNCTIONAL = 3