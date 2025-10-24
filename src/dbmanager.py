from src.media_title import MediaTitle
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

class DuplicateMovieError(Exception):
    pass

class DbManager:
    def __init__(self):
        self.conn = psycopg2.connect(database = "moviedb",
            host = "db",
            port = "5432",
            user = db_user,
            password = db_password
        )
        self.cur = self.conn.cursor()

    def add_title(self, title: MediaTitle, my_rating: int):

        # Rating value validation
        if my_rating < 0 or my_rating >= 10:
            raise ValueError("Rating must be between 0 and 10")

        # Checking for existing title
        if self.record_exists(title.imdb_id):
            raise DuplicateMovieError(f"Movie {title.title} already exists in Db")

        # Movie/Series checking - additional types could be implemented in the future
        t_type = 1 if title.title_type == "movie" else 2

        # Db INSERT
        try:
            # INSERT into 'titles' table
            self.cur.execute(
                """
                INSERT INTO titles (title, year, runtime, poster, plot, awards, imdb_rating, imdbID, type_id,
                    my_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING title_id
                """,
                (title.title, title.year, title.runtime, title.poster, title.plot, title.awards,
                 title.imdb_rating, title.imdb_id, t_type, my_rating)
            )
            title_id = self.cur.fetchone()[0]


            # INSERT into 'people' table
            # ACTORS
            actors = []
            for actor in title.actors:
                self.cur.execute("SELECT person_id FROM people WHERE name = %s;", (actor,))
                row = self.cur.fetchone()
                if row is not None:
                    person_id = row[0]
                else:
                    self.cur.execute("INSERT INTO people (name) VALUES (%s) RETURNING person_id", (actor,))
                    person_id = self.cur.fetchone()[0]
                actors.append(person_id)

            # WRITERS / CREATORS
            writers = []
            for writer in title.writers:
                self.cur.execute("SELECT person_id FROM people WHERE name = %s;", (writer,))
                row = self.cur.fetchone()
                if row is not None:
                    person_id = row[0]
                else:
                    self.cur.execute("INSERT INTO people (name) VALUES (%s) RETURNING person_id", (writer,))
                    person_id = self.cur.fetchone()[0]
                writers.append(person_id)

            # DIRECTORS
            # I think that it's possible that some title would have more than one director so...
            directors = []
            if title.director != "N/A":
                for director in title.director:
                    self.cur.execute("SELECT person_id FROM people WHERE name = %s;", (director,))
                    row = self.cur.fetchone()
                    if row is not None:
                        person_id = row[0]
                    else:
                        self.cur.execute("INSERT INTO people (name) VALUES (%s) RETURNING person_id", (director,))
                        person_id = self.cur.fetchone()[0]
                    directors.append(person_id)

            # INSERT into 'title_roles' table
            # ACTORS
            for person_id in actors:
                self.cur.execute("INSERT INTO title_roles (title_id, person_id, role) VALUES (%s, %s, %s)",
                                 (title_id, person_id, "actor"))

            # WRITERS / CREATORS
            role = "writer" if t_type == 1 else "creator"
            for person_id in writers:
                self.cur.execute("INSERT INTO title_roles (title_id, person_id, role) VALUES (%s, %s, %s)",
                                 (title_id, person_id, role))

            # DIRECTORS
            if directors:
                for person_id in directors:
                    self.cur.execute("INSERT INTO title_roles (title_id, person_id, role) VALUES (%s, %s, %s)",
                                     (title_id, person_id, "director"))


            # INSERT into 'genres' table
            genres = []
            for genre in title.genre:
                self.cur.execute("SELECT genre_id FROM genres WHERE name = %s;", (genre,))
                row = self.cur.fetchone()
                if row is not None:
                    genre_id = row[0]
                else:
                    self.cur.execute("INSERT INTO genres (name) VALUES (%s) RETURNING genre_id", (genre,))
                    genre_id = self.cur.fetchone()[0]
                genres.append(genre_id)

            # INSERT into 'title_genres' table
            for genre in genres:
                self.cur.execute("INSERT INTO title_genres (title_id, genre_id) VALUES (%s, %s)",
                                 (title_id, genre,))

            # INSERT into 'countries' table
            countries = []
            for country in title.country:
                self.cur.execute("SELECT country_id FROM countries WHERE name = %s;", (country,))
                row = self.cur.fetchone()
                if row is not None:
                    country_id = row[0]
                else:
                    self.cur.execute("INSERT INTO countries (name) VALUES (%s) RETURNING country_id", (country,))
                    country_id = self.cur.fetchone()[0]
                countries.append(country_id)

            # INSERT into 'title_countries' table
            for country in countries:
                self.cur.execute("INSERT INTO title_countries (title_id, country_id) VALUES (%s, %s)",
                                 (title_id, country))

            # If everything is fine...
            self.conn.commit()

        except Exception as e:
            # При любой ошибке — откат
            self.conn.rollback()
            raise e


    def get_title_by_name(self, title):
        pass

    def get_titles_by_rating(self):
        pass

    def get_all_titles(self):
        pass

    def search_title_by_name(self, search_str: str):
        pass

    def update_title(self, title):
        pass

    def update_rating(self, title):
        pass

    def delete_title(self, title):
        pass

    def record_exists(self, imdb_id:str) -> bool:
        self.cur.execute("SELECT 1 FROM titles WHERE imdb_id = %s;", (imdb_id,))
        return self.cur.fetchone() is not None

    def execute(self, query: str, params: tuple = ()):
        pass

    def close(self):
        self.cur.close()
        self.conn.close()