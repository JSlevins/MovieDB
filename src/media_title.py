class MediaTitle:
    """Class represents a media title (movie, series, etc.) with attributes, and methods for JSON/YAML serialization."""

    def __init__(self, title, year, director, writers, poster, genre, runtime, actors, plot, awards, country, imdbid,
                 imdb_rating, title_type, my_rating=None):

        # Checking required fields for not None
        if None in (title, year, director, imdbid, imdb_rating):
            missing = [name for name, val in zip(("title", "year", "director", "imdbid", "imdb_rating"),
            (title, year, director, imdbid, imdb_rating)) if val is None]
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        self.title = title
        self.year = year
        self.director = self._list_parsing(director)
        self.writers = self._list_parsing(writers)
        self.poster = poster
        self.genre = self._list_parsing(genre)
        self.runtime = runtime
        self.actors = self._list_parsing(actors)
        self.plot = plot
        self.awards = awards
        self.country = self._list_parsing(country)
        self.imdbid = imdbid
        self.imdb_rating = imdb_rating
        self.title_type = title_type
        self.my_rating = my_rating or 0

    @classmethod
    def from_dict(cls, data: dict):
        #Creating an instance from json
        return cls(
            title=data.get("Title"),
            year=data.get("Year"),
            director=data.get("Director"),
            writers=data.get("Writer"),
            poster=data.get("Poster"),
            genre=data.get("Genre"),
            runtime=data.get("Runtime"),
            actors=data.get("Actors"),
            plot=data.get("Plot"),
            awards=data.get("Awards"),
            country=data.get("Country"),
            imdb_rating=data.get("imdbRating"),
            imdbid=data.get("imdbID"),
            title_type=data.get("Type"),
            my_rating=data.get("MyRating"),
        )

    @staticmethod
    def _list_parsing(string: str) -> list:
        return string.split(", ")

    def __str__ (self):
        return f"'{self.title}' {self.year}"
    __repr__ = __str__