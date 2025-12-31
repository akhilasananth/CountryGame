import re
from unittest.mock import mock_open, patch

import pytest

from countrygame.constants import NUMBER_OF_NEW_LINES, ComputerMoveResult, PlayerStatus
from countrygame.game import CountryChainGame


@pytest.fixture
def setup_game(mocker):
    game = CountryChainGame()
    mock_print = mocker.patch("builtins.print")
    return game, mock_print


def test_load_countries():
    mock_data = "Italy\nIndia\nIceland\n"
    with patch("builtins.open", mock_open(read_data=mock_data)):
        game = CountryChainGame()

    assert "italy" in game.all_countries
    assert "india" in game.all_countries
    assert "iceland" in game.all_countries
    assert "i" in game.unseen_countries
    assert game.unseen_countries["i"] == {"italy", "india", "iceland"}


def test_load_countries_file_not_found():
    countries_file_path = "fake/path.txt"
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError, match=re.escape("was not found")):
            CountryChainGame(countries_file_path)


def test_empty_lines_are_skipped():
    mock_data = "\n\nIndia\n\n\n\n\n\n\n\n\n\n\n\nGermany\n"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        game = CountryChainGame("fake/path.txt")

    assert game.all_countries == {"india", "germany"}


def test_forbidden_separators_mark_invalid():
    mock_data = "India\nUSA,Canada\nFrance|Spain\nGermany;Uruguay\n"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        game = CountryChainGame("fake/path.txt")

    assert game.all_countries == {"india"}
    assert "USA,Canada" in game.invalid_countries
    assert "France|Spain" in game.invalid_countries
    assert "Germany;Uruguay" in game.invalid_countries


def test_no_valid_countries_raises():
    mock_data = "\n\nUSA,Canada\nFrance|Spain\n"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        with pytest.raises(ValueError, match="No valid countries found in the file"):
            game = CountryChainGame("fake/path.txt")
            print(game.all_countries)


def test_is_valid_country():
    game = CountryChainGame()
    game.all_countries = {"italy", "france"}

    assert game.is_valid_country("italy")
    assert not game.is_valid_country("germany")


def test_validate_and_remove_country_valid():
    game = CountryChainGame()
    game.all_countries = {"italy", "ireland"}
    game.unseen_countries = {
        "i": {"italy", "ireland"},
    }

    result = game.get_player_status("italy", "i")

    assert result is PlayerStatus.CONTINUE
    assert "italy" not in game.unseen_countries["i"]


def test_validate_and_remove_country_invalid():
    game = CountryChainGame()
    game.all_countries = {"italy"}
    game.unseen_countries = {"i": {"italy"}}

    result = game.get_player_status("huihiu", "h")

    assert result is PlayerStatus.RETRY


def test_validate_and_remove_country_None():
    game = CountryChainGame()
    game.all_countries = {"italy"}
    game.unseen_countries = {"i": {"italy"}}

    result = game.get_player_status("", " ")

    assert result is PlayerStatus.RETRY


def test_validate_and_remove_country_empty_set():
    game = CountryChainGame()
    game.all_countries = {"italy"}
    game.unseen_countries = {"i": {}}

    result = game.get_player_status("italy", "i")

    assert result is PlayerStatus.LOSE


def test_validate_and_remove_country_first_round():
    game = CountryChainGame()
    game.all_countries = {"italy"}
    game.unseen_countries = {"i": {"italy"}}

    result = game.get_player_status("italy", " ")

    assert result is PlayerStatus.CONTINUE


def test_validate_and_remove_country_invalid_first_char():
    game = CountryChainGame()
    game.all_countries = {"italy"}
    game.unseen_countries = {"i": {"italy"}}

    result = game.get_player_status("italy", "j")

    assert result is PlayerStatus.LOSE


def test_get_computer_response():
    game = CountryChainGame()
    game.unseen_countries = {"y": {"yemen", "yugoslavia"}}

    country = game.get_computer_response("Italy")
    assert country in {"yemen", "yugoslavia"}
    assert country not in game.unseen_countries["y"]


def test_get_computer_response_empty_set():
    game = CountryChainGame()
    game.unseen_countries = {"y": set()}
    country = "Italy"

    result = game.get_computer_response(country)
    assert result is None


def test_get_computer_response_missing_input():
    game = CountryChainGame()
    game.unseen_countries = {"y": {"yemen"}}
    country = ""

    result = game.get_computer_response(country)
    assert result is None


def test_play_get_player_input(setup_game, mocker):
    game, mock_print = setup_game
    mocker.patch("builtins.input", side_effect=["", "india"])
    result = game.play_get_player_input()
    mock_print.assert_any_call("Input cannot be empty. 🗑️")
    assert result == "india"


def test_play_handle_player_move_lose(setup_game):
    game, mock_print = setup_game
    result = game.play_handle_player_move("ireland", "d")

    mock_print.assert_any_call(
        "❌This country was already said or it has the wrong first letter. You Lose! 😢"
    )
    assert result == PlayerStatus.LOSE


def test_play_handle_player_move_retry(setup_game):
    game, mock_print = setup_game
    result = game.play_handle_player_move("sdfsfds", "i")

    mock_print.assert_any_call("⚠️Invalid country, please try again! 🙃")
    assert result == PlayerStatus.RETRY


def test_play_handle_player_move_quit(setup_game):
    game, mock_print = setup_game
    result = game.play_handle_player_move("quit", "i")

    mock_print.assert_any_call("🪦 Bye! Game ended.")
    assert result == PlayerStatus.QUIT


def test_play_handle_player_move_continue(setup_game):
    game, mock_print = setup_game
    game.all_countries = {"italy", "ireland"}
    game.unseen_countries = {
        "i": {"italy", "ireland"},
    }
    result = game.play_handle_player_move("italy", "i")

    mock_print.assert_any_call("✅ Accepted! Last letter is y")
    assert result == PlayerStatus.CONTINUE


def test_play_handle_computer_move_empty_set(setup_game):
    game, mock_print = setup_game
    game.all_countries = {"italy", "ireland"}
    game.unseen_countries = {
        "i": {},
    }

    result = game.play_handle_computer_move("Brunei")
    mock_print.assert_any_call(
        "No more countries that start with the letter: i 😢. You win! 😃🎉"
    )
    assert result == ComputerMoveResult(PlayerStatus.WIN, None)


def test_play_handle_computer_move_empty_player_input(setup_game):
    game, mock_print = setup_game
    game.all_countries = {"italy", "ireland"}
    game.unseen_countries = {
        "i": {"italy"},
    }

    result = game.play_handle_computer_move("")
    mock_print.assert_any_call("Cannot respond to empty player response")
    assert result == ComputerMoveResult(PlayerStatus.RETRY, None)


def test_play_handle_computer_move_valid(setup_game):
    game, mock_print = setup_game
    game.all_countries = {"italy", "ireland"}
    game.unseen_countries = {
        "i": {"italy"},
    }

    result = game.play_handle_computer_move("Brunei")
    mock_print.assert_any_call("> 🤖Computer: italy")
    assert result == ComputerMoveResult(PlayerStatus.CONTINUE, "y")


def test_play_invalid_countries_printed(setup_game):
    game, mock_print = setup_game
    game.all_countries = {"india"}
    game.invalid_countries = {"USA,Canada", "France|Spain", "Germany;Uruguay"}

    game.print_welcome_message()

    mock_print.assert_any_call(
        f"The following invalid countries were not counted: {game.invalid_countries}"
    )


def test_clear_console_tty_true(setup_game, mocker):
    game, mock_print = setup_game
    mock_stdout = mocker.patch("sys.stdout")
    mock_stdout.isatty.return_value = True
    game.clear_console()
    mock_print.assert_called_once_with("\033[2J\033[H", end="")


def test_clear_console_tty_false(setup_game, mocker):
    game, mock_print = setup_game
    mock_stdout = mocker.patch("sys.stdout")
    mock_stdout.isatty.return_value = False

    game.clear_console()

    mock_print.assert_called_once_with("\n" * NUMBER_OF_NEW_LINES)


def test_reset_all_rebuilds_unseen_countries(setup_game):
    game, _ = setup_game

    game.all_countries = {"india", "italy", "germany"}
    game.unseen_countries = {"i": {"italy"}}

    game.reset_all()

    expected = {
        "i": {"india", "italy"},
        "g": {"germany"},
    }

    assert dict(game.unseen_countries) == expected
