from src.dbmanager import DbManager
from src.media_title import MediaTitle
from typing import Tuple, Optional

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
        self.stage = 0
        self.media = None
        self.client = OMDbClient()
        self.dbm = DbManager()
        self.actions = []  ### temp placeholder ###
        #     (func, func_dest, menu_stage)
        # ]

    # Menu
    def show_menu(self) -> None:
        """ Print the menu for current CLI stage with header and list of actions. """
        # Print header
        self.stage_message()

        # Make and print menu list
        menu_list = [el for el in self.actions if el[2] == self.stage]
        for i, (_, description) in enumerate(menu_list, start=1):
            print(f"[{i}] {description}")

    def run(self) -> None:
        """ Main function. """
        while True:
            self.show_menu()
            choice = input("\nEnter number: ")
            if not choice.isdigit() and choice not in QUIT_SET:
                print("\nInvalid input. Please enter a number.")
                continue
            choice = int(choice)
            if choice in QUIT_SET:
                # Quit sequence
                break
            if 1 <= choice <= len(self.actions):
                func = self.actions[choice - 1][0]
                func()
            else:
                print("\nInvalid choice. Please enter a valid number.")

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
        if self.stage == 1: msg = "Main"  # Main menu
        elif self.stage == 2: msg = "OMDb"  # OMDb menu
        elif self.stage == 3 or self.stage == 6: msg = f'"{self.media.title}"({self.media.year})'  # OMDb / Db media menu
        elif self.stage == 4: msg = "My Database"  # Db menu
        elif self.stage == 5: msg = "Search results:"  # Db multiple media menu
        else: msg = "Secret level!!!"  # I have no idea how could you end here

        print('\n' + '-' * 50 + '\n')
        print(msg.center(50) + '\n')

    def search_omdb(self):
        self.stage = 2
        self.run()
    def search_db(self):
        self.stage = 4
        self.run()

    def omdb_get_media_by_title(self) -> None:
        """Search title by name in OMDb and manage errors."""
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
            self.run()

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
                return self.run()

            except (ValueError, OMDbNotFoundError) as e:
                print(e)
                stdin = input("Press any key to try again...\nOr type 'q' for quit: ")
                if stdin in QUIT_SET:
                    return self.quit()

            except OMDbError as e:
                print(e)
                print('Due to error, returning to main menu.')
                self.stage = 1
                return self.run()

    def print_search_results(self, data: dict) -> None: pass
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