from functools import partial
from typing import List, Tuple, Callable, Optional

from src.dbmanager import DbManager
from src.media_title import MediaTitle
from src.omdb_client import OMDbClient, OMDbError, OMDbNotFoundError

QUIT_SET = {'q', 'Q', 'exit'}

class CLI:
    """
    CLI class for MovieDb.

    Handles user interaction, parses input, manages a single MediaTitle instance,
    and orchestrates calls to DbManager, MediaTitle, OMDbClient and Exporter while providing
    consistent error handling and user feedback.
    """
    def __init__(self):

        self.client: OMDbClient = OMDbClient()
        self.dbm: DbManager = DbManager()
        self.stage: int = 0
        self.media: Optional[MediaTitle] = None
        self.functions: List[Tuple[Callable, str, int]] = []  ### temp placeholder ### (func, func_dest, menu_stage)
        self.actions: List[Tuple[Callable, str]] = []

    # Menu
    def show_menu(self) -> None:
        """ Print the menu for current CLI stage with header and list of actions. """
        # Print header
        self.stage_message()

        # Make and print menu list
        self.actions = [el for el in self.functions if el[2] == self.stage]

        # Format width of menu counter
        results_len = len(self.actions)
        if results_len < 10: n_width = 1
        elif results_len < 100: n_width = 2
        else: n_width = 3

        for i, (_, description, _) in enumerate(self.actions, start=1):
            print(f"[{i:>{n_width}}] {description}")

        print(f'\n[{0:>{n_width}}] Go back to previous menu')
        print(f'[{"'q'":>{n_width}}] Exit')

    def run_action(self, search_flag: Optional[bool] = None) -> None:
        """ Main function. """
        while True:
            # Do not show menu on search results
            if not search_flag:
                self.show_menu()

            # Validation input check
            choice = input("\nEnter number: ")
            if not choice.isdigit() and choice not in QUIT_SET:
                print("\nInvalid input. Please enter a number.")
                continue

            # Quit input check
            if choice in QUIT_SET:
                return self.quit()

            # 'Go back' input check
            choice = int(choice)
            if choice == 0:
                return self.go_back()

            # Correct input check and run actions
            if 1 <= choice <= len(self.actions):
                func = self.actions[choice - 1][0]
                return func()
            else:
                print("\nInvalid choice. Please enter a valid number.")
                continue

    # Messages
    def intro_message(self) -> None:
        """ Print intro message. """
        # Message on utility launch
        print('\n' + '#' * 50 + '\n#' + ' ' * 48 + '#')
        print('#' + "Welcome to MovieDb".center(48) + '#')
        print('#' + ' ' * 48 + '#\n' + '#' * 50)
        self.stage = 1

    def stage_message(self) -> None:
        """ Print the header for the current CLI stage. """
        # Set header
        stage_header = {
            1: "Main menu",
            2: "OMDb",
            3: f'"{self.media.title}"({self.media.year})',
            4: "My Database",
            5: "Search results",
            6: f'"{self.media.title}"({self.media.year})'
        }
        msg = stage_header.get(self.stage)

        # Print header
        print('\n' + '-' * 50 + '\n')
        print(msg.center(50) + '\n')

    # From main menu
    def search_omdb(self) -> None:
        self.stage = 2
        self.run_action()

    def search_db(self) -> None:
        self.stage = 4
        self.run_action()

    # From OMDb menu
    def omdb_get_media_by_title(self) -> None:
        """ Search title by name in OMDb and manage errors. """
        print('\n' + '-' * 50 + '\n')
        title_name = input("Enter title: ")

        try:
            # Trying to get title from OMDb by exact name
            data = self.client.get_title_by_name(title_name)

            # Create MediaTitle from data
            self.media = MediaTitle.from_dict(data)
            print(self.media.title)

            # Update CLI stage and proceed
            self.stage = 3
            self.run_action()

        except OMDbNotFoundError:
            # If there's no such title, trying to search
            data = self.client.search_title(title_name)
            self.stage = 5
            self.print_search_results(data)

        except OMDbError as e:
            print(e)
            stdin = input("Press any key to continue...\nOr type 'q' for quit: ")
            if stdin in QUIT_SET:
                quit()
            self.go_back()

    def omdb_get_media_by_imdbid(self) -> None:
        """Search title by imdbID in OMDb and manage errors."""
        while True:
            print('\n' + '-' * 50 + '\n')
            title_id = input("Enter imdbID of a title. Expected format: 'tt1234567': ")

            try:
                # Trying to get title from OMDb by imdbID
                data = self.client.get_title_by_imdbid(title_id)
                # Create MediaTitle from data
                self.media = MediaTitle.from_dict(data)
                print(self.media.title)

                # Update CLI stage
                self.stage = 3
                return self.run_action()

            except (ValueError, OMDbNotFoundError) as e:
                print(e)
                stdin = input("Press any key to try again...\nOr type 'q' for quit: ")
                if stdin in QUIT_SET:
                    return self.quit()

            except OMDbError as e:
                print(e)
                print('Due to error, returning to main menu.')
                self.stage = 1
                return self.run_action()

    #Universal method
    def print_search_results(self, data: dict[str, list[dict[str, str]]]) -> None:
        """ Print search results. """
        # Print header
        self.stage_message()

        ### Setup menu before printing
        results = data["Search"]  # list of dict (search result titles)

        # Make self.action list
        self.actions = []
        for result in results:
            # Format string
            title_str = result.get('Title')
            year_str = result.get('Year')
            imdb_id_str = result.get('imdbID')
            description = f'{title_str:<50} {year_str:<6} {imdb_id_str}'

            self.actions.append((partial(self.client.get_title_by_imdbid, imdb_id_str), description))

        ### Print menu
        # Format width of menu counter
        results_len = len(results)
        if results_len < 10: n_width = 1
        elif results_len < 100: n_width = 2
        else: n_width = 3

        # Print self.action list
        for i, (_, description) in enumerate(self.actions, start=1):
            print(f'[{i:>{n_width}}] {description}')
        # Print Go back and exit cases
        print(f'\n[{0:>{n_width}}] Go back to previous menu')
        print(f'[{"q":>{n_width}}] Exit')

        self.run_action(search_flag=True)

    def db_get_media_by_title(self): pass
    def db_get_media_by_id(self): pass
    def db_show_all_media(self): pass
    def db_show_media_by_rating(self): pass
    def omdb_add_to_db(self): pass
    def media_show(self): pass
    def media_update_rating(self): pass
    def save_json(self): pass
    def save_yaml(self): pass

    def go_back(self): pass
    def quit(self): pass