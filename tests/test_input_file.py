from pathlib import Path

import pytest


@pytest.fixture
def countries_file():
    project_root = Path(__file__).resolve().parent.parent
    return Path(project_root / "data" / "countries.txt")


def test_countries_file_exists(countries_file):
    assert countries_file.exists(), "Countries file does not exist"


def test_countries_file_is_txt(countries_file):
    assert countries_file.suffix == ".txt", "Countries file is not a .txt file"


def test_countries_file_not_empty(countries_file):
    content = countries_file.read_text().strip()
    assert content, "Countries file is empty"


def test_countries_file_has_valid_entries(countries_file):
    lines = [line.strip() for line in countries_file.read_text().splitlines()]

    assert len(lines) > 0
    assert all(lines), "One or more country entries are empty or there is an empty line"


def test_countries_are_newline_separated(countries_file):
    content = countries_file.read_text().strip()

    lines = content.splitlines()
    assert len(lines) > 1, "Countries must be listed on separate lines"

    forbidden_separators = [",", "|", ";", "\t"]
    for sep in forbidden_separators:
        assert sep not in content, f"Countries must not be '{sep}' separated"
