import pytest
from unittest.mock import MagicMock, patch

from src.cli import CLI

@pytest.fixture
def cli():
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

def test_launch_menu_navigation(cli):
    """ Launch menu check. """
    cli.stage = 1
    cli.intro_message()

    # Input tests
    with patch("builtins.input", side_effect=["1"]):
        cli.run_action()
    cli.search_omdb.assert_called_once()

    with patch("builtins.input", side_effect=["2"]):
        cli.run_action()
    cli.search_db.assert_called_once()

    with patch("builtins.input", side_effect=["q"]):
        cli.run_action()
    cli.quit.assert_called_once()

def test_state_messages_and_lists(cli):
    """ Check that menu headers and function lists print correctly for each CLI stage; output is inspected manually. """
    for cli.stage in range(1, 7):
        cli.show_menu()