import functools
import os
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.cli import CLI
from src.dbmanager import DbMovieNotFoundError
from src.media_title import MediaTitle
from src.omdb_client import OMDbNotFoundError


# FIXTURES
@pytest.fixture
def cli_mock():
    cli_instance = CLI()

    # Replace external dependencies with mocks
    cli_instance.client = MagicMock()
    cli_instance.dbm = MagicMock()
    cli_instance.media = MagicMock()

    # Replace CLI methods with mocks
    cli_instance.search_omdb = MagicMock()
    cli_instance.search_db = MagicMock()
    cli_instance.go_back = MagicMock()
    cli_instance.quit = MagicMock()

    cli_instance.init_functions()
    return cli_instance

@pytest.fixture(scope="module")
def cli_real():
    cli_instance = CLI()
    cli_instance.init_functions()
    return cli_instance

@pytest.fixture(scope='module')
def media_title():
    path = Path(__file__).parent / "test_movie.json"
    with path.open('r', encoding="utf-8") as f:
        media = json.load(f)
    return MediaTitle.from_dict(media)

@pytest.fixture
def fake_folder():
    """ Fake folder fixture creation and deletion. """
    path = Path.cwd() / "FakeFolder"
    path.mkdir(exist_ok=True)
    (path / "occupied.json").touch()
    yield str(path)

    if os.path.exists(path):
        shutil.rmtree(path)

@pytest.fixture
def fake_list():
    """ Fake list of titles. """
    fake_list = {
      "Search": [
        {
          "Title": "Inception",
          "Year": "2010",
          "imdbID": "tt1375666",
          "Type": "movie",
          "Poster": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg"
        },
        {
          "Title": "Inception: The Cobol Job",
          "Year": "2010",
          "imdbID": "tt5295894",
          "Type": "movie",
          "Poster": "https://m.media-amazon.com/images/M/MV5BMjE0NGIwM2EtZjQxZi00ZTE5LWExN2MtNDBlMjY1ZmZkYjU3XkEyXkFqcGdeQXVyNjMwNzk3Mjk@._V1_SX300.jpg"
        },
        {
          "Title": "The Crack: Inception",
          "Year": "2019",
          "imdbID": "tt6793710",
          "Type": "movie",
          "Poster": "https://m.media-amazon.com/images/M/MV5BZTc4MDliNjAtYmU4YS00NmQzLWEwNjktYTQ2MGFjNDc5MDhlXkEyXkFqcGc@._V1_SX300.jpg"
        },
        {
          "Title": "Inception: Jump Right Into the Action",
          "Year": "2010",
          "imdbID": "tt5295990",
          "Type": "movie",
          "Poster": "https://m.media-amazon.com/images/M/MV5BZGFjOTRiYjgtYjEzMS00ZjQ2LTkzY2YtOGQ0NDI2NTVjOGFmXkEyXkFqcGdeQXVyNDQ5MDYzMTk@._V1_SX300.jpg"
        },
        {
          "Title": "Inception: Motion Comics",
          "Year": "2010–",
          "imdbID": "tt1790736",
          "Type": "series",
          "Poster": "https://m.media-amazon.com/images/M/MV5BNGRkYzkzZmEtY2YwYi00ZTlmLTgyMTctODE0NTNhNTVkZGIxXkEyXkFqcGdeQXVyNjE4MDMwMjk@._V1_SX300.jpg"
        },
        {
          "Title": "Inception",
          "Year": "2014",
          "imdbID": "tt7321322",
          "Type": "movie",
          "Poster": "https://m.media-amazon.com/images/M/MV5BOTY3OGFlNTktYTJiZi00ZWMxLTk4MjQtNmJiODkxYThiNjg4XkEyXkFqcGc@._V1_SX300.jpg"
        },
        {
          "Title": "Madness Inception",
          "Year": "2022",
          "imdbID": "tt29258696",
          "Type": "movie",
          "Poster": "N/A"
        },
        {
          "Title": "Inception: 4Movie Premiere Special",
          "Year": "2010",
          "imdbID": "tt1686778",
          "Type": "movie",
          "Poster": "N/A"
        },
        {
          "Title": "Cyberalien: Inception",
          "Year": "2017",
          "imdbID": "tt7926130",
          "Type": "movie",
          "Poster": "N/A"
        },
        {
          "Title": "WWA: The Inception",
          "Year": "2001",
          "imdbID": "tt0311992",
          "Type": "movie",
          "Poster": "https://m.media-amazon.com/images/M/MV5BNTEyNGJjMTMtZjZhZC00ODFkLWIyYzktN2JjMTcwMmY5MDJlXkEyXkFqcGdeQXVyNDkwMzY5NjQ@._V1_SX300.jpg"
        }
      ],
      "totalResults": "38",
      "Response": "True"
    }
    return fake_list

# TESTS
def test_launch_menu_navigation(cli_mock):
    """ Launch menu check. """
    cli = cli_mock
    cli.stage = 1

    # Inputs for all actions in sequence
    with patch("builtins.input", side_effect=["1", "2", "q"]):
        cli.run_action()  # '1'
        cli.run_action()  # '2'
        cli.run_action()  # 'Q'

    cli.search_omdb.assert_called_once()  # type: ignore
    cli.search_db.assert_called_once()  # type: ignore
    cli.quit.assert_called_once()  # type: ignore

    # Additionally check for "Q"
    cli.quit.reset_mock()  # type: ignore
    with patch("builtins.input", side_effect=["Q"]):
        cli.run_action()  # 'q'
    cli.quit.assert_called_once()  # type: ignore

@pytest.mark.skip(reason="Manual inspection only, skipping for now")
def test_state_messages_and_lists(cli):
    """ Check that menu headers and function lists print correctly for each CLI stage; output is inspected manually. """
    for cli.stage in range(1, 7):
        cli.show_menu()

def test_rating_input_valid_and_invalid(cli_real, monkeypatch):
    """Checks that the function prompts again for invalid input and returns the correct value."""

    # Sequence of inputs:
    # "abc" → not a number → input is requested again
    # "15", "-1", "5.5" → out of valid range or type → input is requested again
    # "8", "0", "10" → valid inputs, returned by the function

    cli = cli_real
    inputs = iter(["abc", "15", "8", "-1", "5.5", "0", "10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result1 = cli._rating_input()
    assert result1 == "8"
    result2 = cli._rating_input()
    assert result2 == "0"
    result3 = cli._rating_input()
    assert result3 == "10"

def test_path_handler_empty_input(cli_real, media_title, fake_folder):
    """ Test for empty path handler inputs"""
    cli = cli_real
    cli.media = media_title

    # Test empty inputs
    with patch("builtins.input", side_effect=["", ""]):
        with patch("os.getcwd", return_value=fake_folder):
            result = cli._path_handler('json')
            path = os.getcwd()


    expected_path = os.path.join(path, "Inception.json")
    assert result == expected_path

def test_path_handler_file_exists_cases(cli_real, media_title, fake_folder):
    """Test file naming when the file already exists. Checks invalid input handling and creating a copy afterward."""
    cli = cli_real
    cli.media = media_title

    with patch("builtins.input", side_effect=["", "occupied", "abc", "", "occupied", "c"]):
        with patch("os.getcwd", return_value=fake_folder):
            result = cli._path_handler('json')
            path = os.getcwd()
            print(path)

    expected_path = os.path.join(path, "occupied_1.json")
    assert result == expected_path

def test_go_back_cases(cli_real):
    """ Test go back cases. """
    cli = cli_real

    # stage = 5 from_db = True --> 4
    cli.stage = 5
    cli.from_db = True
    cli.go_back()
    assert cli.stage == 4

    # stage = 5 from_db = False --> 2
    cli.stage = 5
    cli.from_db = False
    cli.go_back()
    assert cli.stage == 2

    # stage = 3 --> 2
    cli.stage = 3
    cli.go_back()
    assert cli.stage == 2

    # stage = 6 --> 1
    cli.stage = 6
    cli.go_back()
    assert cli.stage == 1

def test_print_search_results_fake_list(cli_mock, fake_list):
    """ Test printing search results when list is present. """
    cli = cli_mock
    # Check if from_db flag is True. No reason to check both
    cli.from_db = True
    cli.print_search_results(fake_list)

    assert len(cli.actions) == len(fake_list["Search"])
    for (action, description), result in zip(cli.actions, fake_list["Search"]):
        # Проверяем, что action — это partial от нужного метода
        assert isinstance(action, functools.partial)
        if cli.from_db:
            assert action.func == cli.dbm.get_title_by_imdbid
        else:
            assert action.func == cli.client.get_title_by_imdbid
        # Проверяем описание
        assert result['Title'] in description
        assert result['Year'] in description
        assert result['imdbID'] in description

def test_print_search_results_empty_list(cli_mock):
    """ Test printing search results when list is empty. """
    cli = cli_mock
    empty_list = {"Search": []}

    with patch("builtins.print") as mock_print:
        cli.print_search_results(empty_list)

    mock_print.assert_any_call("\nNothing was found...")
    assert len(cli.actions) == len(empty_list["Search"])

def test_omdb_not_found_error(cli_mock, fake_list):
    """ Test that OMDb proceeds to returns error when omdb is not available.
        Same sequence for DbMovieNotFoundError. """
    cli = cli_mock

    # Mocks and data
    cli.client.get_title_by_name = MagicMock(side_effect=OMDbNotFoundError)
    cli.client.search_title.return_value = fake_list
    cli.print_search_results = MagicMock()

    with patch("builtins.input", return_value="Some Title"):
        cli.omdb_get_media_by_title()

    cli.client.get_title_by_name.assert_called_once_with("Some Title")
    cli.client.search_title.assert_called_once_with("Some Title")  # type: ignore
    cli.print_search_results.assert_called_once_with(fake_list)
    assert cli.stage == 5
    assert cli.from_db is False

def test_db_movie_not_found_error(cli_mock, fake_list):
    cli = cli_mock

    # Mocks and data
    cli.dbm.get_title_by_name = MagicMock(side_effect=DbMovieNotFoundError)
    cli.dbm.search_titles_by_name.return_value = fake_list["Search"]
    cli.print_search_results = MagicMock()

    with patch("builtins.input", return_value="Another Title"):
        cli.db_get_media_by_title()

    cli.dbm.get_title_by_name.assert_called_once_with("Another Title")
    cli.dbm.search_titles_by_name.assert_called_once_with("Another Title")  # type: ignore
    cli.print_search_results.assert_called_once()
    assert cli.stage == 5
    assert cli.from_db is True
