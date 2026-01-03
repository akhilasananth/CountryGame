import re
import pytest
from unittest.mock import mock_open, patch
from countrygame.constants import NUMBER_OF_NEW_LINES, MoveResult, PlayerStatus, MAX_INVALID_INPUTS
from countrygame.game import CountryChainGame


@pytest.fixture
def setup_game(mocker):
    game = CountryChainGame()
    mock_print = mocker.patch("builtins.print")
    return game, mock_print

# test helpers

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
    assert 'USA,Canada' in game.invalid_countries
    assert 'France|Spain' in game.invalid_countries
    assert 'Germany;Uruguay' in game.invalid_countries

def test_play_invalid_countries_printed(setup_game):
    game, mock_print = setup_game
    game.all_countries = {"india"}
    game.invalid_countries = {"USA,Canada", "France|Spain", "Germany;Uruguay"}

    game._print_welcome_message()

    mock_print.assert_any_call(
        f"The following invalid countries were not counted: {game.invalid_countries}"
    )

def test_no_valid_countries():
    mock_data = "\n\nUSA,Canada\nFrance|Spain\n"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        with pytest.raises(ValueError, match="🪦 No valid countries found in the file. 😢"):
            game = CountryChainGame("fake/path.txt")
            print(game.all_countries)

def test_is_valid_country():
    game = CountryChainGame()
    game.all_countries = {"italy", "france"}

    assert game._is_valid_country("italy")
    assert not game._is_valid_country("germany")

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

    game._reset_all()

    expected = {
        "i": {"india", "italy"},
        "g": {"germany"},
    }

    assert dict(game.unseen_countries) == expected

# test game

def test_invalid_last_character(setup_game):
    game, _ = setup_game

    with pytest.raises(ValueError, match="The last character cannot be more than 1 character long"):
        game._get_player_move("ssdff", MAX_INVALID_INPUTS)

def test_max_invalid_inputs(setup_game, mocker):
    game, mock_print = setup_game
    empty_inputs = ["" for _ in range(MAX_INVALID_INPUTS)]
    mocker.patch("builtins.input", side_effect=empty_inputs)
    result = game._get_player_move("s", MAX_INVALID_INPUTS)

    assert result == MoveResult(PlayerStatus.LOSE, None)
    mock_print.assert_any_call("🪦 Max invalid attempts reached 😢")

def test_player_move_quit(setup_game, mocker):
    game, mock_print = setup_game

    mocker.patch("builtins.input", side_effect=["quit"])
    result = game._get_player_move("o", MAX_INVALID_INPUTS)

    mock_print.assert_any_call("🪦 Bye! Game ended.")
    assert result == MoveResult(PlayerStatus.QUIT, None)

def test_player_move_restart(setup_game, mocker):
    game, mock_print = setup_game

    mocker.patch("builtins.input", side_effect=["restart"])
    result = game._get_player_move("o", MAX_INVALID_INPUTS)

    mock_print.assert_any_call("🔄 Game restarted!")
    assert result == MoveResult(PlayerStatus.RESTART, None)

def test_player_move_empty(setup_game, mocker):
    game, mock_print = setup_game
    game.all_countries = {"italy"}
    game.unseen_countries = {"i": {"italy"}}

    invalid_inputs = [" "] * MAX_INVALID_INPUTS
    mocker.patch("builtins.input", side_effect=invalid_inputs)

    result = game._get_player_move("i", MAX_INVALID_INPUTS)

    mock_print.assert_any_call(
        f"🗑️ Input cannot be empty. 💀You have {MAX_INVALID_INPUTS-1} tries left."
    )
    assert result == MoveResult(PlayerStatus.LOSE, None)

def test_player_move_invalid(setup_game, mocker):
    game, mock_print = setup_game
    game.all_countries = {"italy", "ireland", "germany"}
    game.unseen_countries = {"i": {"italy", "ireland"}}

    invalid_inputs = ["sdfnkjsd"] * MAX_INVALID_INPUTS
    mocker.patch("builtins.input", side_effect=invalid_inputs)

    result = game._get_player_move("i", MAX_INVALID_INPUTS)

    mock_print.assert_any_call(
        f"⚠️ Invalid country! 💀You have {MAX_INVALID_INPUTS - 1} tries left."
    )
    assert result == MoveResult(PlayerStatus.LOSE, None)

def test_player_move_wrong_first_letter(setup_game, mocker):
    game, mock_print = setup_game

    # Mock input to give a country with the wrong first letter
    mocker.patch("builtins.input", side_effect=["algeria"])

    # Call the function
    result = game._get_player_move(last_letter="i", attempts_left=MAX_INVALID_INPUTS)

    # Check that the wrong-letter print happened
    mock_print.assert_any_call("❌ Wrong starting letter! You lose! 😢")

    # Check that the function returned a lose MoveResult
    assert result == MoveResult(PlayerStatus.LOSE, None)

def test_player_move_already_used(setup_game, mocker):
    game, mock_print = setup_game
    game.all_countries = {"italy", "ireland", "germany"}
    game.unseen_countries = {"i": {"ireland"}}

    mocker.patch("builtins.input", side_effect=["italy"])

    result = game._get_player_move("i", MAX_INVALID_INPUTS)

    assert result == MoveResult(PlayerStatus.LOSE, None)
    mock_print.assert_any_call("❌ Country already used! You lose! 😢")

def test_player_move_valid(setup_game, mocker):
    game, mock_print = setup_game
    game.all_countries = {"italy", "ireland", "germany"}
    game.unseen_countries = {"i": {"italy", "ireland"}}

    mocker.patch("builtins.input", side_effect=["italy"])

    result = game._get_player_move("i", MAX_INVALID_INPUTS)

    assert result == MoveResult(PlayerStatus.CONTINUE, 'y')
    mock_print.assert_any_call(f"✅ Accepted! Last letter is y")
    assert "italy" not in game.unseen_countries["i"]

def test_player_move_no_countries_left(setup_game):
    game, mock_print = setup_game
    game.all_countries = {"italy"}
    game.unseen_countries = {"i": {}}

    result = game._get_player_move("i", MAX_INVALID_INPUTS)

    assert result == MoveResult(PlayerStatus.LOSE, None)
    mock_print.assert_any_call(f"🪦 Sorry you're out of luck! No more countries start with the letter i 😢")

def test_computer_move_valid(setup_game):
    game, mock_print = setup_game
    game.all_countries = {"yemen", "yugoslavia"}
    game.unseen_countries = {"y": {"yemen", "yugoslavia"}}

    result = game._get_computer_move("y")
    assert result.status == PlayerStatus.CONTINUE
    assert result.last_letter in {'n', 'a'}

# Not sure when this would happen
def test_computer_move_empty_last_letter(setup_game):
    game, mock_print = setup_game

    result = game._get_computer_move('')
    assert result == MoveResult(PlayerStatus.RETRY, None)

def test_computer_move_no_countries_left(setup_game, mocker):
    game, mock_print = setup_game
    game.unseen_countries = {"y": set()}

    result = game._get_computer_move('y')
    assert result == MoveResult(PlayerStatus.WIN, None)
