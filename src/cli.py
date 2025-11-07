import os
import re
import sys
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
        # External clients (init later)
        self.client: OMDbClient | None = None
        self.dbm: DbManager | None = None

        # Internal state
        self.stage: int = 1
        self.media: Optional[MediaTitle] = None
        self.from_db: bool = False  # Navigation purpose
        self.actions: List[Tuple[Callable, str]] = []
        # self.search_flag = False

        # Menu functions (init later)
        self.functions: List[Tuple[Callable, str, int]] = []  # (func, func_dest, menu_stage)

    # Init methods
    def init_clients(self) -> None:
        """ Initialize external clients and DB connection. """
        self.client: OMDbClient = OMDbClient()
        self.dbm: DbManager = DbManager()

    def init_functions(self) -> None:
        """ Initialize functions. """
        self.functions: List[Tuple[Callable, str, int]] = [
            (self.search_omdb, "Search in OMDb", 1),
            (self.search_db, "Search in My Database", 1),
            (self.omdb_get_media_by_title, "Get media by title", 2),
            (self.omdb_get_media_by_imdbid, "Get media by imdbID", 2),
            (self.omdb_add_to_db, "Add media to My Database", 3),
            (self.db_get_media_by_title, "Get media by title", 4),
            (self.db_get_media_by_imdbid, "Get media by imdbID", 4),
            (self.db_show_all_media, "Show all media in My Database", 4),
            (self.db_show_media_by_rating, "Show all high rated media", 4),
            (self.media_show, "Show full media info", 6),
            (self.media_update_rating, "Update rating", 6),
            (self.save_json, "Save to JSON", 6),
            (self.save_yaml, "Save to YAML", 6)
        ]


    # Menu
    def show_menu(self) -> None:
        """ Main function. Print the menu for current CLI stage with header and list of actions. """
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

        print('\n')
        if not self.stage == 1:
            print(f'[{0:>{n_width}}] Go back to previous menu')

        print(f'[{"q":>{n_width}}] Exit')

    # Main loop
    def run_action(self) -> None:
        """ Main loop. Parse menu navigation inputs. """
        while True:
            # Do not show menu on search results
            # if not self.search_flag:
            #     self.show_menu()

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
    @staticmethod
    def intro_message() -> None:
        """ Main function. Print intro message. """
        # Message on utility launch
        print('\n' + '#' * 50 + '\n#' + ' ' * 48 + '#')
        print('#' + "Welcome to MovieDb".center(48) + '#')
        print('#' + " " * 48 + '#')
        print('#' + "Made by JSlevins".center(48) + '#')
        print('#' + ' ' * 48 + '#\n' + '#' * 50)

    def stage_message(self) -> None:
        """ Main function. Print the header for the current CLI stage. """
        # Set header
        stage_header = {
            1: "Main menu",
            2: "OMDb",
            3: f"OMDb\n'{self.media.title}' ({self.media.year})",
            4: "My Database",
            5: "Search results",
            6: f"My Database\n'{self.media.title}' ({self.media.year})"
        }
        msg = stage_header.get(self.stage)

        # Print header
        print('\n' + '-' * 50 + '\n')
        for line in msg.splitlines():
            print(line.center(50))
        print('\n')

    # OMDb methods
    def omdb_get_media_by_title(self) -> None:
        """ Stage 2. Search title by name in OMDb and manage errors. """
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

        except OMDbNotFoundError:
            # If there's no such title, trying to search
            data = self.client.search_title(title_name)
            # Continue to search results
            self.stage = 5
            self.from_db = False
            self.print_search_results(data)

        except OMDbError as e:
            print(e)
            stdin = input("Press any key to continue...\nOr type 'q' for quit: ")
            if stdin in QUIT_SET:
                quit()
            self.go_back()

    def omdb_get_media_by_imdbid(self) -> None:
        """ Stage 2. Search title by imdbID in OMDb and manage errors."""

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

        except (ValueError, OMDbNotFoundError) as e:
            print(e)

        except OMDbError as e:
            print(e)
            print('Due to error in OMDb, returning to main menu.')
            self.stage = 1

    def omdb_add_to_db(self) -> None:
        """ Stage 3: Add title to my database."""
        print("\nSaving media to database...")
        rating = input("Enter rating (0-10): ")
        if not self._rating_input_validation(rating):
            return
        else:
            try:
                result = self.dbm.add_title(self.media, rating)
                if result:
                    print(f"'{self.media.title}' has been successfully saved to the database.")
                    self.stage = 6

            except DbDuplicateMovieError:
                print("This media already exists in database.")
                self.stage = 6

            except Exception as e:
                print(f"Something went wrong: {e}")

    # DB methods
    def db_get_media_by_title(self) -> None:
        """ Stage 4. Search title by name in Db and manage errors. """
        print('\n' + '-' * 50 + '\n')
        title_name = input("\nEnter title: ")

        try:
            # Trying to get title from OMDb by exact name
            data = self.dbm.get_title_by_name(title_name)

            self.media = MediaTitle.from_dict(data)
            print(f"\n{self.media}")

            #Update CLI stage and proceed
            self.stage = 6

        except DbMovieNotFoundError:
            # If there's no such title, trying to search in Database
            print("\nMovie not found. Continue to search...\n")
            data = self.dbm.search_titles_by_name(title_name)

            # Formating data
            data = {"Search": data}

            # Continue to search results
            self.stage = 5
            self.from_db = True
            self.print_search_results(data)

        except Exception as e:
            print(e)

    def db_get_media_by_imdbid(self) -> None:
        """ Stage 4. Search title by imdbID in Db and manage errors. """
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

        except (ValueError, DbMovieNotFoundError) as e:
            print(e)

        except Exception as e:
            print(e)
            print('Due to error, returning to main menu.')
            self.stage = 1

    def db_show_all_media(self) -> None:
        """ Stage 4. Show all media titles from the Db. """
        # Retrieve all metia titles
        data = self.dbm.get_all_titles()

        # Formating data
        data = {"Search": data}

        # Continue to search results
        self.stage = 5
        self.from_db = True
        self.print_search_results(data)

    def db_show_media_by_rating(self) -> None:
        """ stage 4. Show all media titles from the Db by rating equal or above present. """
        rating = input("\nEnter minimum rating (0-10): ")
        if self._rating_input_validation(rating):
            data = self.dbm.get_titles_by_rating(rating)
            data = {"Search": data}
            self.stage = 5
            self.from_db = True
            self.print_search_results(data)

    #Universal methods
    def print_search_results(self, data: dict[str, list[dict[str, str]]]) -> None:
        """ Main function for stage 5. Print search results. """
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

            if self.from_db:
                self.actions.append((partial(self.dbm.get_title_by_imdbid, imdb_id_str), description))
            else:
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

    def media_show(self) -> None:
        """ Stage 6. Print FULL information about actual media title. """
        print('\n' + '-' * 75 + '\n')
        year_and_runtime = f"{self.media.year}   -({self.media.runtime})-"
        title = f"'{self.media.title}'"
        print(f"{title.center(75)}")
        print(f"{year_and_runtime.center(75)}")
        rating = f"""IMDb Rating: {self.media.imdb_rating}/10 | My Rating: {self.media.my_rating}/10 | IMDbID: {self.media.imdbid}"""
        print(f"{rating.center(75)}")
        print('\n' + '-' * 75 + '\n')
        if self.media.title_type == 'movie':
            suf = '' if len(self.media.director) == 1 else 's'
            print(f"Director{suf}: {self.media.director}")
            suf = '' if len(self.media.writers) == 1 else 's'
            print(f"Writer{suf}: {self.media.writers}")
        else:
            suf = '' if len(self.media.writers) == 1 else 's'
            print(f"Creator{suf}: {self.media.writers}")
        print(f"Actors: {self.media.actors}")
        print(f"\nGenre: {self.media.genre}")
        print(f"Plot: {self.media.plot}")
        label = 'Country' if len(self.media.country) == 1 else 'Countries'
        print(f"\n{label}: {self.media.country}")
        print(f"Awards: {self.media.awards}")

    def media_update_rating(self) -> None:
        """ Stage 6. Update user rating for media title. """
        rating = input("\nEnter new rating (0-10): ")
        if self._rating_input_validation(rating):
            try:
                result = self.dbm.update_rating(self.media.imdbid, rating)
                if result:
                    print("\nMedia title has been updated.")
                else:
                    print("\nSomething went wrong.")

            except Exception as e:
                print(e)
                stdin = input("Press 'enter' to try again...\nOr type 'q' for quit: ")
                if stdin in QUIT_SET:
                    self.quit()

    def save_json(self) -> None:
        """ Stage 6. Save media title to JSON. """
        full_path = self._path_handler('json')

        exporter = Exporter(self.media, full_path)
        try:
            result = exporter.to_json()
            if result:
                print("File has been saved.")
        except OSError as e:
            print(f"Failed to save JSON: {e}")

    def save_yaml(self) -> None:
        """ Stage 6. Save media title to YAML. """
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
        """ Stage 1. Search OMDb. """
        self.stage = 2

    def search_db(self) -> None:
        """ Stage 1. Search DB. """
        self.stage = 4

    def go_back(self) -> None:
        """ Main function. Stage all except 1. Make 'return' to different menu stage. Depends on stage """
        back_menu = {
            1: 1,  # Main menu
            2: 1,  # From OMDb to main menu
            3: 2,  # From 'OMDb media title'  to OMDb menu
            4: 1,  # From MyDb to main menu
            6: 1  # From 'media title' menu to main menu
        }

        # Check 'from_db' flag for stage = 5 case
        if self.stage == 5:
            # From Search Results to OMDb menu or MyDb menu
            self.stage = 4 if self.from_db else 2
        else:
            self.stage = back_menu[self.stage]

    def quit(self) -> None:
        """ Main Function. Close DbManager connection and exit application. """
        print("\nExiting MovieDb. Goodbye!")

        #Close DbManager connection
        try:
            self.dbm.close()
        except Exception as e:
            print(f"Failed to close database: {e}")

        sys.exit(0)

    # Inner methods
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
        def is_valid_path(p: str) -> bool:
            # Check for invalid characters in the path (Windows)
            invalid_chars = r'<>:"|?*'
            return not any(char in p for char in invalid_chars)

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