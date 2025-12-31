import sys
from pathlib import Path

from countrygame.constants import NUMBER_OF_NEW_LINES


def get_path(file_path: str):
    project_root = Path(__file__).resolve().parent.parent
    return Path(project_root / file_path)


def clear_console():
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")
    else:
        print("\n" * NUMBER_OF_NEW_LINES)
