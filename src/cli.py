from src.media_title import MediaTitle
from typing import Tuple, Optional


class CLI:
    """
    CLI class for MovieDb.

    Handles user interaction, parses input, manages a single MediaTitle instance,
    and orchestrates calls to DbManager, MediaTitle, OMDbClient and Exporter while providing
    consistent error handling and user feedback.
    """
    def __init__(self, level = 0):
        self.level = level
        # self.commands = [
        #     (func_name, "func_desc", menu_level)
        # ]

    # Menu
    def show_menu(self):
        print("Welcome to MovieDb.")
        for i, (_, description) in enumerate(self.commands, start=1):
            print(f"[{i}] {description}")

    def run(self):
        while True:
            self.show_menu()
            choice = input("\nEnter number: ")
            if not choice.isdigit():
                print("\nInvalid input. Please enter a number.")
                continue
            choice = int(choice)
            if 1 <= choice <= len(self.commands):
                func = self.commands[choice - 1][0]
                func()
            else:
                print("\nInvalid choice. Please enter a valid number.")