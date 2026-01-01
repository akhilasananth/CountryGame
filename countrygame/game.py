import random
from collections import defaultdict
from pathlib import Path

from countrygame.constants import (
    FORBIDDEN_SEPARATORS, ComputerMoveResult, PlayerStatus, MAX_EMPTY_INPUTS
)
from countrygame.utils import clear_console, get_path


class CountryChainGame:

    def __init__(
        self, countries_file_path_str="data/countries.txt", clear_fn=clear_console
    ):
        self.clear_console = clear_fn
        self.unseen_countries = defaultdict(
            set
        )  # unseen_countries tracks remaining playable countries
        self.all_countries = set()
        self.invalid_countries = (
            set()
        )  # to show what countries were not added to all_countries from the file
        self._load_all_countries(get_path(countries_file_path_str))

    # HELPERS

    def _load_all_countries(self, countries_file_path: Path) -> None:
        try:
            with open(countries_file_path, "r") as f:
                for line in f:
                    country = line.strip()
                    # Skip empty lines
                    if not country:
                        continue
                    # Skip lines with forbidden separators
                    if any(sep in country for sep in FORBIDDEN_SEPARATORS):
                        self.invalid_countries.add(country)
                        continue
                    # Normalize
                    country = country.lower()
                    self.all_countries.add(country)
                    self.unseen_countries[country[0]].add(country)

            if not self.all_countries:
                raise ValueError("No valid countries found in the file")

        except FileNotFoundError:
            raise FileNotFoundError(
                f"The file '{countries_file_path}' was not found."
            )  # game cannot start without this

    def _is_valid_country(self, country: str) -> bool:
        return country in self.all_countries

    def _reset_all(self) -> None:
        self.unseen_countries = defaultdict(set)
        for country in self.all_countries:
            self.unseen_countries[country[0]].add(country)

    # PRINTING HELPERS

    def _get_player_input(self) -> str | None:
        empty_attempts = MAX_EMPTY_INPUTS
        while empty_attempts != 0:
            player_input = input("> 🧑‍🎤Input country: ").strip().lower()
            if not player_input:
                print("Input cannot be empty. 🗑️")
                empty_attempts -= 1
            else:
                return player_input

        print("🪦 Max empty inputs - 3 reached 😢")
        return None

    def _handle_player_move(
        self, player_input: str, computer_last_letter: str
    ) -> PlayerStatus:
        status = self.get_player_status(player_input, computer_last_letter)

        if status == PlayerStatus.LOSE:
            print(
                "❌This country was already said or it has the wrong first letter. You Lose! 😢"
            )
        elif status == PlayerStatus.RETRY:
            print("⚠️Invalid country, please try again! 🙃")
        elif status == PlayerStatus.QUIT:
            print("🪦 Bye! Game ended.")
        else:
            last_letter = player_input[-1].lower()
            print(f"✅ Accepted! Last letter is {last_letter}")

        return status

    def _handle_computer_move(self, player_input: str) -> ComputerMoveResult:
        if not player_input:
            print("Cannot respond to empty player response")
            return ComputerMoveResult(PlayerStatus.RETRY, None)

        computer_response = self.get_computer_response(player_input)

        if not computer_response:
            player_last_letter = player_input[-1].lower()
            print(
                f"No more countries that start with the letter: {player_last_letter} 😢. You win! 😃🎉"
            )
            return ComputerMoveResult(PlayerStatus.WIN, None)
        else:
            print(f"> 🤖Computer: {computer_response}")
            return ComputerMoveResult(
                PlayerStatus.CONTINUE, computer_response[-1].lower()
            )

    def _print_welcome_message(self) -> None:
        print(
            f""" Welcome to the Country Chain Game! 👋🏼
            Rules:
            - Enter a country starting with the last letter of the previous country.
            - No repeats allowed. Repeating a country = you lose.
            - Also responding with a country with the wrong first letter = you lose.
            - To Quit, type: 'quit'
            - To Restart the game, type: 'restart'
            - You go first. 
            - Please note that the game quits after {MAX_EMPTY_INPUTS} empty inputs
                """
        )

        if self.invalid_countries:
            print(
                f"The following invalid countries were not counted: {self.invalid_countries}"
            )

    # CORE

    def get_player_status(
        self, player_input: str, computer_last_letter: str
    ) -> PlayerStatus:
        if not player_input:
            return PlayerStatus.QUIT

        if player_input == "quit":
            return PlayerStatus.QUIT

        elif player_input == "restart":
            return PlayerStatus.RESTART

        # Checking if the input is a country name
        country = player_input.lower().strip()

        if not self._is_valid_country(country):
            return PlayerStatus.RETRY

        first_letter = country[0]
        computer_last_letter = computer_last_letter.strip()

        # after the first round in the game
        if len(computer_last_letter) != 0 and first_letter != computer_last_letter:
            return PlayerStatus.LOSE

        if country not in self.unseen_countries[first_letter]:
            return PlayerStatus.LOSE

        # Remove the country from unseen as the country is now seen
        self.unseen_countries[first_letter].remove(country)

        return PlayerStatus.CONTINUE

    def get_computer_response(self, country: str) -> str | None:
        if not country:
            return None

        last_letter = country[-1].lower()

        if not self.unseen_countries[last_letter]:
            return None

        ret_country = random.choice(
            list(self.unseen_countries[last_letter])
        )  # less deterministic than using pop
        self.unseen_countries[last_letter].remove(ret_country)

        return ret_country

    def run_game(self) -> PlayerStatus | None:
        self._print_welcome_message()
        computer_last_letter = ""

        while True:
            player_input = self._get_player_input()

            if player_input == "restart":
                self._reset_all()
                clear_console()
                print("🔄 Game restarted!\n")
                return PlayerStatus.RESTART

            status = self._handle_player_move(player_input, computer_last_letter)
            if status == PlayerStatus.LOSE or status == PlayerStatus.QUIT:
                return status

            elif status == PlayerStatus.RETRY:
                continue

            computer_response = self._handle_computer_move(player_input)
            computer_last_letter = computer_response.last_letter
            if computer_last_letter is None:
                return computer_response.status

    def play(self) -> None:
        while True:
            if self.run_game() != PlayerStatus.RESTART:
                break


if __name__ == "__main__":
    CountryChainGame().play()
