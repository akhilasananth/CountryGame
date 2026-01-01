from dataclasses import dataclass
from enum import Enum

FORBIDDEN_SEPARATORS = {",", "|", ";", "\t"}
NUMBER_OF_NEW_LINES = 100
MAX_EMPTY_INPUTS = 3

class PlayerStatus(Enum):
    WIN = 1
    LOSE = 2
    CONTINUE = 3
    RETRY = 4
    QUIT = 5
    RESTART = 6


@dataclass
class ComputerMoveResult:
    status: PlayerStatus
    last_letter: str | None
