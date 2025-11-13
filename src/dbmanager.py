import os
import re
import time

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from src.media_title import MediaTitle


load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

class DbDuplicateMovieError(Exception): pass
class DbMovieNotFoundError(Exception): pass

class DbManager:
    """
    DbManagement — manages the movie database, handling connections, queries, and CRUD operations.
    Provides methods to add, fetch, search, and filter movies while ensuring transactional safety.
    """

    def __init__(self, database = "moviedb", host = "db", port = "5432", user = db_user, password = db_password):
        self.conn = psycopg2.connect(
            database = database,
            host = host,
            port = port,
            user = user,
            password = password
        )
        self.cur = self.conn.cursor(cursor_factory = RealDictCursor)

    def add_title(self, title: MediaTitle, my_rating: str) -> bool:
        # Checking for existing title
        if self.query_record_exist_imdbid(title.imdbid):
            raise DbDuplicateMovieError(f"Movie {title.title} already exists in Db")

        # Adding title to Db
        query = self.query_add_title(title, my_rating)
        return query

    def get_title_by_imdbid(self, imdbid) -> dict[str, str] | None :
        # Format checking
        if not re.fullmatch(r"tt\d{7,9}", imdbid):
            raise ValueError("Invalid IMDb ID format. Expected format: 'tt123456789'")

        # Checking if movie exists
        if self.query_record_exist_imdbid(imdbid):
            return self.query_get_title_by_imdbid(imdbid)

        else:
            raise DbMovieNotFoundError(f"Title with IMDbID {imdbid} not found.")

    def get_title_by_name(self, title_name) -> dict[str, str] | None:
        imdbid = self.query_get_title_by_name(title_name)
        if imdbid:
            return self.get_title_by_imdbid(imdbid)
        else:
            raise DbMovieNotFoundError(f"Title with name {title_name} not found.")

    def get_titles_by_rating(self, my_rating: str) -> list[dict[str, str]]:
        """
        Get list of MediaTitles from Db that has my_rating equal to or greater than presented
        :return: list[MediaTitle]: List of MediaTitle objects
         or above presented
        """
        # Getting list of imdbIDs
        query = self.query_get_titles_by_rating(my_rating)

        # Returning list of MediaTitles
        return [self.get_title_by_imdbid(imdbid) for imdbid in query] if query else []

    def get_all_titles(self) -> list[dict[str, str]]:
        """
        Get all titles from Db
        :return: list[MediaTitle]: List of MediaTitle objects
        """
        # Getting list of imdbIDs
        query = self.query_get_all_titles()

        # Returning list of MediaTitles
        return [self.get_title_by_imdbid(imdbid) for imdbid in query] if query else []

    def search_titles_by_name(self, substring: str) -> list[dict[str, str]]:
        """
        Search titles by partial name.
        :return: list[MediaTitle]: List of MediaTitle objects
        """
        # Getting list of imdbIDs that match the pattern 'substring'
        query = self.query_search_titles_by_name(substring)

        # Returning list of MediaTitles
        return [self.get_title_by_imdbid(imdbid) for imdbid in query] if query else []

    def update_rating(self, imdbid: str, rating: str):
        # Format checking
        if not re.fullmatch(r"tt\d{7,9}", imdbid):
            raise ValueError("Invalid IMDb ID format. Expected value: 'tt0000000'")

        # Updating rating in Db
        return self.query_update_rating(imdbid, rating)

    # def delete_title(self, title):
    #     """
    #     Placeholder function: 'maybe' planned for future implementation.
    #     Currently not used.
    #     """
    #     pass

    def query_add_title(self, title: MediaTitle, my_rating: str) -> bool:
        # Movie/Series checking - additional types could be implemented in the future
        t_type = 1 if title.title_type == "movie" else 2

        # Db INSERT
        try:
            # INSERT into 'titles' table
            self.cur.execute(
                """INSERT INTO titles (title, year, runtime, poster, plot, awards, imdb_rating, imdbID, type_id, my_rating) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING title_id""",
                (title.title, title.year, title.runtime, title.poster, title.plot, title.awards,
                 title.imdb_rating, title.imdbid, t_type, my_rating)
            )
            title_id = self.cur.fetchone()['title_id']

            # INSERT into 'people' table
            # ACTORS
            actors = []
            for actor in title.actors:
                self.cur.execute("SELECT person_id FROM people WHERE name = %s;", (actor,))
                row = self.cur.fetchone()
                if row is not None:
                    person_id = row['person_id']
                else:
                    self.cur.execute("INSERT INTO people (name) VALUES (%s) RETURNING person_id", (actor,))
                    person_id = self.cur.fetchone()['person_id']
                actors.append(person_id)

            # WRITERS / CREATORS
            writers = []
            for writer in title.writers:
                self.cur.execute("SELECT person_id FROM people WHERE name = %s;", (writer,))
                row = self.cur.fetchone()
                if row is not None:
                    person_id = row['person_id']
                else:
                    self.cur.execute("INSERT INTO people (name) VALUES (%s) RETURNING person_id", (writer,))
                    person_id = self.cur.fetchone()['person_id']
                writers.append(person_id)

            # DIRECTORS
            # I think that it's possible that some title would have more than one director so...
            directors = []
            if title.director != "N/A":
                for director in title.director:
                    self.cur.execute("SELECT person_id FROM people WHERE name = %s;", (director,))
                    row = self.cur.fetchone()
                    if row is not None:
                        person_id = row['person_id']
                    else:
                        self.cur.execute("INSERT INTO people (name) VALUES (%s) RETURNING person_id", (director,))
                        person_id = self.cur.fetchone()['person_id']
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
                    genre_id = row['genre_id']
                else:
                    self.cur.execute("INSERT INTO genres (name) VALUES (%s) RETURNING genre_id", (genre,))
                    genre_id = self.cur.fetchone()['genre_id']
                genres.append(genre_id)

            # INSERT into 'title_genres' table
            for genre in genres:
                self.cur.execute("INSERT INTO title_genres (title_id, genre_id) VALUES (%s, %s)", (title_id, genre,))

            # INSERT into 'countries' table
            countries = []
            for country in title.country:
                self.cur.execute("SELECT country_id FROM countries WHERE name = %s;", (country,))
                row = self.cur.fetchone()
                if row is not None:
                    country_id = row['country_id']
                else:
                    self.cur.execute("INSERT INTO countries (name) VALUES (%s) RETURNING country_id", (country,))
                    country_id = self.cur.fetchone()['country_id']
                countries.append(country_id)

            # INSERT into 'title_countries' table
            for country in countries:
                self.cur.execute("INSERT INTO title_countries (title_id, country_id) VALUES (%s, %s)",
                                 (title_id, country))

            # If everything is fine...
            self.conn.commit()
            return True

        except Exception as e:
            # If any exception -> rollback
            self.conn.rollback()
            raise e

    def query_get_titles_by_rating(self, my_rating: str) -> list[str]:
        self.cur.execute("SELECT imdbid from titles WHERE my_rating >= %s", (my_rating,))
        rows = self.cur.fetchall()
        return [row["imdbid"] for row in rows]

    def query_get_all_titles(self) -> list[str]:
        self.cur.execute("SELECT imdbid FROM titles")
        rows = self.cur.fetchall()
        return [row["imdbid"] for row in rows]

    def query_get_title_by_name(self, title_name: str) -> str | None:
        # Returns imdbID if it finds title or None if it's not
        self.cur.execute("SELECT imdbid FROM titles WHERE LOWER(title) = LOWER(%s);", (title_name,))
        rows = self.cur.fetchall()
        if rows:
            return rows[0]["imdbid"]
        else: return None

    def query_get_title_by_imdbid(self, imdbid) -> dict:
        self.cur.execute("""SELECT
                    t.title AS "Title", 
                    t.year AS "Year", 
                    t.poster AS "Poster", 
                    t.runtime AS "Runtime", 
                    t.plot AS "Plot", 
                    t.awards AS "Awards", 
                    t.imdbid AS "imdbID", 
                    t.imdb_rating AS "imdbRating", 
                    ty.name AS "Type", 
                    t.my_rating AS "MyRating",
                    -- s.status_id AS "Status", 
                    -- list of genres as comma-separated string
                    COALESCE(STRING_AGG(DISTINCT g.name, ', '), '{}') AS "Genre",
                    -- list of countries as comma-separated string
                    COALESCE(STRING_AGG(DISTINCT c.name, ', '), '{}') AS "Country",
                    -- lists of directors as comma-separated string
                    COALESCE(STRING_AGG(DISTINCT p.name, ', ') FILTER (WHERE tr.role = 'director'), '{}') AS "Director",
                    -- lists of actors as comma-separated string
                    COALESCE(STRING_AGG(DISTINCT p.name, ', ') FILTER (WHERE tr.role = 'actor'), '{}') AS "Actors",
                    -- lists of writers as comma-separated string
                    COALESCE(STRING_AGG(DISTINCT p.name, ', ') FILTER (WHERE tr.role IN ('writer', 'creator')), '{}') AS "Writer"
                    FROM titles t
                        JOIN types ty ON t.type_id = ty.type_id 
                     -- JOIN statuses s ON t.status_id = s.status_id
                        JOIN title_genres tg ON t.title_id = tg.title_id
                        JOIN genres g ON tg.genre_id = g.genre_id
                        JOIN title_countries tc ON t.title_id = tc.title_id
                        JOIN countries c ON tc.country_id = c.country_id
                        JOIN title_roles tr ON t.title_id = tr.title_id
                        JOIN people p ON tr.person_id = p.person_id
                    WHERE t.imdbid = %s
                    GROUP BY t.title, t.year, t.runtime, t.poster, t.plot, t.awards, t.imdb_rating, t.imdbID, ty.name, t.my_rating; --s.name 
                    """, (imdbid,))
        return dict(self.cur.fetchone())

    def query_search_titles_by_name(self, substring) -> list[str]:
        self.cur.execute("SELECT imdbid FROM titles WHERE title ILIKE %s;", (f"%{substring}%",))
        rows = self.cur.fetchall()
        return [row["imdbid"] for row in rows]

    def query_update_rating(self, imdbid: str, rating: str) -> bool:
        try:
            self.cur.execute("UPDATE titles SET my_rating = %s WHERE imdbid = %s;", (rating, imdbid))
            self.conn.commit()
            return self.cur.rowcount == 1

        except Exception as e:
            # If any exception -> rollback
            self.conn.rollback()
            raise e

    def query_record_exist_imdbid(self, imdbid:str) -> bool:
        # Returns TRUE if movie exists
        self.cur.execute("SELECT 1 FROM titles WHERE imdbID = %s;", (imdbid,))
        return self.cur.fetchone() is not None

    def close(self):
        self.cur.close()
        self.conn.close()