import os
import re
from functools import partial
from typing import List, Tuple, Callable, Optional

from src.dbmanager import DbManager, DbDuplicateMovieError, DbMovieNotFoundError
from src.exporter import Exporter
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

            choice = input("\nEnter number: ")

            # Validation input check
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

    # OMDb methods
    def omdb_get_media_by_title(self) -> None:
        """ Search title by name in OMDb and manage errors. """
        print('\n' + '-' * 50 + '\n')
        title_name = input("Enter title: ")

        try:
            # Trying to get title from OMDb by exact name
            data = self.client.get_title_by_name(title_name)

            # Create MediaTitle from data
            self.media = MediaTitle.from_dict(data)
            print(f"\n{self.media}")

            # Update CLI stage and proceed
            self.stage = 3
            self.run_action()

        except OMDbNotFoundError:
            # If there's no such title, trying to search
            data = self.client.search_title(title_name)
            # Continue to search results
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
            title_id = input("Enter imdbID of a title. Expected format: 'tt123456789': ")

            try:
                # Trying to get title from OMDb by imdbID
                data = self.client.get_title_by_imdbid(title_id)
                # Create MediaTitle from data
                self.media = MediaTitle.from_dict(data)
                print(f"\n{self.media}")

                # Update CLI stage
                self.stage = 3
                return self.run_action()

            except (ValueError, OMDbNotFoundError) as e:
                print(e)
                stdin = input("Press any key to try again...\nOr type 'q' for quit: ")
                if stdin in QUIT_SET:
                    return self.quit()
                continue

            except OMDbError as e:
                print(e)
                print('Due to error, returning to main menu.')
                self.stage = 1
                return self.run_action()

    def omdb_add_to_db(self): pass

    # DB methods
    def db_get_media_by_title(self) -> None:
        """ Search title by name in Db and manage errors. """
        print('\n' + '-' * 50 + '\n')
        title_name = input("\nEnter title: ")

        try:
            # Trying to get title from OMDb by exact name
            data = self.dbm.get_title_by_name(title_name)

            self.media = MediaTitle.from_dict(data)
            print(f"\n{self.media}")

            #Update CLI stage and proceed
            self.stage = 6
            self.run_action()

        except DbMovieNotFoundError:
            # If there's no such title, trying to search in Database
            print("\nMovie not found. Continue to search...\n")
            data = self.dbm.search_titles_by_name(title_name)

            # Formating data
            data = {"Search": data}

            # Continue to search results
            self.stage = 5
            self.print_search_results(data)

        except Exception as e:
            print(e)
            stdin = input("\nPress any key to continue...\nOr type 'q' for quit: ")
            if stdin in QUIT_SET:
                quit()
            self.go_back()  # Maybe I should implement "Try Again" here...

    def db_get_media_by_id(self) -> None:
        """ Search title by imdbID in Db and manage errors. """
        while True:
            print('\n' + '-' * 50 + '\n')
            title_id = input("Enter imdbID of a title. Expected format: 'tt123456789': ")

            try:
                # Trying to get title from Db by imdbID
                data = self.dbm.get_title_by_imdbid(title_id)
                # Create MediaTitle from data
                self.media = MediaTitle.from_dict(data)
                print(f"\n{self.media}")

                # Update CLI stage
                self.stage = 6
                return self.run_action()

            except (ValueError, DbMovieNotFoundError) as e:
                print(e)
                stdin = input("Press any key to try again...\nOr type 'q' for quit: ")
                if stdin in QUIT_SET:
                    return self.quit()
                continue

            except Exception as e:
                print(e)
                print('Due to error, returning to main menu.')
                self.stage = 1
                return self.run_action()

    def db_show_all_media(self) -> None:
        """ Show all media titles from the Db. """
        # Retrieve all metia titles
        data = self.dbm.get_all_titles()

        # Formating data
        data = {"Search": data}

        # Continue to search results
        self.stage = 5
        self.print_search_results(data)

    def db_show_media_by_rating(self) -> None:
        """ Show all media titles from the Db by rating equal or above present. """
        while True:
            rating = input("\nEnter minimum rating (0-10): ")

            # Validation input check
            if not self._rating_input_validation(rating):
                continue

            rating = int(rating)
            data = self.dbm.get_titles_by_rating(rating)
            data = {"Search": data}
            self.stage = 5
            return self.print_search_results(data)

    #Universal methods
    def print_search_results(self, data: dict[str, list[dict[str, str]]]) -> None:
        """ Print search results. """
        # Print header
        self.stage_message()

        ### Setup menu before printing
        results = data.get("Search")  # list of dict (search result titles)

        # Checking for empty list
        if len(results) == 0:
            print("\nNothing was found.")

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

    def media_show(self): pass

    def media_update_rating(self) -> None:
        """ Update user rating for media title. """
        while True:
            rating = input("\nEnter new rating (0-10): ")

            # Validation input check
            if not self._rating_input_validation(rating):
                continue

            try:
                result = self.dbm.update_rating(self.media.imdbid, rating)
                if result:
                    print("\nMedia title has been updated.")
                else:
                    print("\nSomething went wrong.")

                # Returning to menu
                return self.run_action()

            except Exception as e:
                print(e)
                stdin = input("Press 'enter' to try again...\nOr type 'q' for quit: ")
                if stdin in QUIT_SET:
                    return self.quit()
                continue

    def save_json(self):
        """ Save media title to JSON. """
        full_path = self._path_handler('json')

        exporter = Exporter(self.media, full_path)
        try:
            result = exporter.to_json()
            if result:
                print("File has been saved.")
        except OSError as e:
            print(f"Failed to save JSON: {e}")

    def save_yaml(self):
        """ Save media title to YAML. """
        full_path = self._path_handler('yaml')

        exporter = Exporter(self.media, full_path)
        try:
            result = exporter.to_yaml()
            if result:
                print("File has been saved.")
        except OSError as e:
            print(f"Failed to save YAML: {e}")

    # Navigation methods
    def search_omdb(self) -> None:
        self.stage = 2
        self.run_action()

    def search_db(self) -> None:
        self.stage = 4
        self.run_action()

    def go_back(self): pass
    def quit(self): pass

    @staticmethod
    def _rating_input_validation(rating: str) -> bool:
        # Validation input check
        if not rating.isdigit():
            print("\nInvalid input. Please enter a number.")
            return False

        rating = int(rating)
        if not 0 <= int(rating) <= 10:
            print("\nInvalid input. Rating must be between 0 and 10.")
            return False

        return True

    def _path_handler(self, ext: str) -> str | None:
        """
        Handles save path. Ask for save path and filename. Set default filename / folder.
        Check if path exists. Check if filename exists. Rewrites or ask for new filename.
        """
        def is_valid_path(path: str) -> bool:
            # Check for invalid characters in the path (Windows)
            invalid_chars = r'<>:"|?*'
            return not any(char in path for char in invalid_chars)

        def get_full_path(self, ext: str) -> str:
            # File type validation
            if ext not in ('json', 'yaml'):
                raise ValueError(f"Unsupported file type: {ext}")

            # Set file type
            if ext == 'json':
                extension = '.json'
            else:
                extension = '.yaml'

            # Create full path with filename
            filename = re.sub(r'[\\/:"*?<>|]+', '_', self.media.title)
            full_path = os.path.join(self.path, filename + extension)
            return full_path

        while True:
            # Directory
            path = input(f"\nEnter folder path to save the JSON file (default: current folder): ").strip()
            if not path:
                path = os.getcwd()

            if not is_valid_path(path):
                print("Invalid folder path. Please avoid <>:\"|?* characters.")
                continue

            if os.path.exists(path):
                if not os.path.isdir(path):
                    print("This is not a folder")
                    continue
            else:
                create = input(f"Folder '{path}' doesn't exist. Create folder? (y/n): ").lower()
                if create == 'y':
                    try:
                        os.makedirs(path, exist_ok=True)
                    except Exception as e:
                        print(f"Failed to create folder '{path}': {e}")
                        continue
                else:
                    continue

            # Filename
            filename = input(f"Enter filename without extension: (default: media title name): ").strip()
            if not filename:
                filename = self.media.title

            filename = re.sub(r'[\\/:"*?<>|]+', '_', filename)

            # Make full path
            full_path = os.path.join(path, filename + '.' + ext)

            # Check if filename already exists
            if os.path.exists(full_path):
                choice = input(f"File '{full_path}' exists. Overwrite (o), copy (c), or re-enter path: ").lower()
                if choice == 'o':
                    return full_path
                elif choice == 'c':
                    counter = 1
                    while True:
                        new_filename = f"{filename}_{counter}.{ext}"
                        new_full_path = os.path.join(path, new_filename)
                        if not os.path.exists(new_full_path):
                            return new_full_path
                        counter += 1
                else:
                    continue
            else:
                return full_path