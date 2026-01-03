import random
from collections import defaultdict
from pathlib import Path

from countrygame.constants import (
    FORBIDDEN_SEPARATORS, MoveResult, PlayerStatus, MAX_INVALID_INPUTS, WELCOME_RULES
)
from countrygame.utils import clear_console, get_path


class CountryChainGame:

    def __init__(
        self, countries_file_path_str="data/countries.txt", clear_fn=clear_console
    ):
        self.clear_console = clear_fn
        self.unseen_countries = defaultdict(set)  # unseen_countries tracks remaining playable countries
        self.all_countries = set()
        self.invalid_countries = set()  # to show what countries were not added to all_countries from the file
        self._load_all_countries(get_path(countries_file_path_str))
        if not self.all_countries:
            raise ValueError("🪦 No valid countries found in the file. 😢")


    # HELPERS

    def _get_input_country(self, line: str) -> None | str:
        """
        Filters what is read from the file with all countries.
        It skips empty lines and lines with forbidden separators.

        :param line: line read from the countries.txt file
        :return: valid country
        """
        country = line.strip()

        # Skip empty lines
        if not country:
            return None
        # Skip lines with forbidden separators
        if any(sep in country for sep in FORBIDDEN_SEPARATORS):
            self.invalid_countries.add(country)
            return None

        return country.lower()

    def _load_all_countries(self, countries_file_path: Path) -> None:
        """
        Initializes all countries
        :param countries_file_path: file containing all countries
        :return: Nothing
        """
        try:
            with open(countries_file_path, "r") as f:
                for line in f:
                    country = self._get_input_country(line)
                    if country is None:
                        continue
                    self.all_countries.add(country)
                    self.unseen_countries[country[0]].add(country)

        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{countries_file_path}' was not found.")

    def _is_valid_country(self, country: str) -> bool:
        """
        Checks if the input country is in the master list of countries
        :param country: country name input by the player
        :return: True if the country is valid and False if it is not a valid country
        """
        return country in self.all_countries

    def _reset_all(self) -> None:
        """
        Re-initializes all countries from the master list of countries
        :return: Nothing
        """
        self.unseen_countries = defaultdict(set)
        for country in self.all_countries:
            self.unseen_countries[country[0]].add(country)

    # GAME

    def _get_player_move(self, last_letter: str, attempts_left: int) -> MoveResult:
        """
        Get the player's move and decide the state.
        Handles MAX_EMPTY_INPUTS + invalid country retries.

        Returns:
            MoveResult(status, last_letter)
        """

        if len(last_letter) > 1:
            raise ValueError("The last character cannot be more than 1 character long")

        # No more countries that start with this last_letter
        # No need to prompt user input
        if last_letter and not self.unseen_countries[last_letter]:
            print(f"🪦 Sorry you're out of luck! No more countries start with the letter {last_letter} 😢")
            return MoveResult(PlayerStatus.LOSE, None)

        while attempts_left > 0:
            player_input = input("> 🧑‍🎤 Input country: ").strip().lower()

            # Quit
            if player_input == "quit":
                print("🪦 Bye! Game ended.")
                return MoveResult(PlayerStatus.QUIT, None)

            # Restart
            if player_input == "restart":
                self._reset_all()
                clear_console()
                print("🔄 Game restarted!")
                return MoveResult(PlayerStatus.RESTART, None)

            # Empty input
            if not player_input:
                attempts_left -= 1
                print(f"🗑️ Input cannot be empty. 💀You have {attempts_left} tries left.")
                continue

            # Invalid country
            if player_input not in self.all_countries:
                attempts_left -= 1
                print(f"⚠️ Invalid country! 💀You have {attempts_left} tries left.")
                continue

            # Wrong first letter
            if last_letter and player_input[0] != last_letter:
                print("❌ Wrong starting letter! You lose! 😢")
                return MoveResult(PlayerStatus.LOSE, None)

            # Already used
            if player_input not in self.unseen_countries[player_input[0]]:
                print("❌ Country already used! You lose! 😢")
                return MoveResult(PlayerStatus.LOSE, None)

            # Valid move
            self.unseen_countries[player_input[0]].remove(player_input)
            print(f"✅ Accepted! Last letter is {player_input[-1]}")
            return MoveResult(PlayerStatus.CONTINUE, player_input[-1])

        print("🪦 Max invalid attempts reached 😢")
        return MoveResult(PlayerStatus.LOSE, None)

    def _get_computer_move(self, last_player_letter: str) -> MoveResult:
        """
        Decide and perform the computer's move based on the input last letter.
        Returns a MoveResult(status, last_letter).
        """
        if not last_player_letter:
            print("Cannot respond to empty player input")
            return MoveResult(PlayerStatus.RETRY, None)

        # Get possible countries starting with the last letter
        available_countries = list(self.unseen_countries[last_player_letter])

        if not available_countries:
            print(f"No more countries that start with the letter '{last_player_letter}' 😢. You win! 😃🎉")
            return MoveResult(PlayerStatus.WIN, None)

        # Pick a random country
        computer_choice = random.choice(available_countries)
        self.unseen_countries[last_player_letter].remove(computer_choice)

        print(f"> 🤖Computer: {computer_choice}")
        return MoveResult(PlayerStatus.CONTINUE, computer_choice[-1].lower())

    def _print_welcome_message(self) -> None:
        """
        This just holds the game rules, it's separated to make the play function look less busy
        :return: Nothing
        """
        print(WELCOME_RULES)

        if self.invalid_countries:
            print(
                f"The following invalid countries were not counted: {self.invalid_countries}"
            )

    def _reset_game_state(self):
        self._print_welcome_message()
        return "", MAX_INVALID_INPUTS

    def play(self) -> None:
        """
        Main play function
        :return: Nothing
        """
        last_letter, attempts_left = self._reset_game_state()

        while True:
            player_result = self._get_player_move(last_letter, attempts_left)

            if player_result.status is PlayerStatus.RESTART:
                last_letter, attempts_left = self._reset_game_state()
                continue

            if player_result.status in (PlayerStatus.QUIT, PlayerStatus.LOSE):
                break

            computer_result = self._get_computer_move(player_result.last_letter)

            if computer_result.status in (PlayerStatus.WIN, PlayerStatus.LOSE):
                break

            last_letter = computer_result.last_letter
            continue


if __name__ == "__main__":
    CountryChainGame().play()
