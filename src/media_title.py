class MediaTitle:
    #Class representing a media title (movie, series, etc.) with attributes, and methods for JSON/YAML serialization.

    def __init__(self, title, year, director, writers, poster, genre, runtime, actors, plot, awards, country, imdb_id,
                 imdb_rating, title_type, my_rating=None):

        # Checking required fields for not None
        if None in (title, year, director, imdb_id, imdb_rating):
            missing = [name for name, val in zip(("title", "year", "director", "imdb_id", "imdb_rating"),
            (title, year, director, imdb_id, imdb_rating)) if val is None]
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        self.title = title
        self.year = year
        self.director = director
        self.writers = writers
        self.poster = poster
        self.genre = genre
        self.runtime = runtime
        self.actors = actors
        self.plot = plot
        self.awards = awards
        self.country = country
        self.imdb_id = imdb_id
        self.imdb_rating = imdb_rating
        self.title_type = title_type
        self.my_rating = my_rating or 0

    @classmethod
    def from_json(cls, data: dict):
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
            imdb_id=data.get("imdbID"),
            title_type=data.get("Type"),
        )

    # @classmethod
    # def from_db(cls, row: tuple):
    #     #Creating an instance from database
    #     (title, year, director, writers, poster, genre, runtime, actors, plot, country, imdb_rating,
    #      imdbID, title_type, my_rating) = row
    #     return cls()

    def __str__ (self):
       pass

    __repr__ = __str__

    def to_json(self):
        pass

    def to_yaml(self):
        pass

    def update_rating(self):
        pass

    def update_status(self):
        pass