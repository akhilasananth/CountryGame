from dataclasses import dataclass
from enum import Enum

FORBIDDEN_SEPARATORS = {",", "|", ";", "\t"}
NUMBER_OF_NEW_LINES = 100
MAX_INVALID_INPUTS = 3
WELCOME_RULES = f""" Welcome to the Country Chain Game! 👋🏼
            Rules:
            - You go first. 
            - To Quit, type: 'quit'.
            - To Restart the game, type: 'restart'.
            - Enter a country starting with the last letter of the previous country.
            - You Lose if you:
                - Repeat a country. 🔁
                - Enter a country that starts with the wrong letter. ❌
                - If there are no other countries left starting with a letter
            - You get {MAX_INVALID_INPUTS} consecutive invalid inputs:
                - Empty input. 🗑️
                - An entry that is not a country. 🌎
            - 🌟WIN: Computer automatically loses if there are no other countries left starting with a letter.
            """

class PlayerStatus(Enum):
    WIN = 1
    LOSE = 2
    CONTINUE = 3
    RETRY = 4
    QUIT = 5
    RESTART = 6


@dataclass
class MoveResult:
    status: PlayerStatus
    last_letter: str | None
