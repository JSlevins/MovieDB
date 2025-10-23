from src.media_title import MediaTitle


class DbManager:
    def __init__(self):
        pass

    def add_title(self, title: MediaTitle):
        pass

    def search_title_by_name(self, search_str: str):
        pass

    def get_title_by_name(self, title):
        pass

    def get_titles_by_rating(self):
        pass

    def get_all_titles(self):
        pass

    def update_title(self, title):
        pass

    def update_rating(self, title):
        pass

    def delete_title(self, title):
        pass

    def execute(self, query: str, params: tuple = ()):
        pass