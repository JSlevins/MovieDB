import json
import pytest

from src.media_title import MediaTitle


@pytest.fixture
def get_movie():
    with open ("tests/test_unit/test_movie.json", "r") as file:
        movie = json.load(file)
    return movie

def test_media_title_init(get_movie):
    media = MediaTitle.from_json(get_movie)

    assert media.title == "Inception"
    assert media.year == "2010"
    assert media.imdbid == "tt1375666"
    assert media.actors == ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"]
    assert media.genre == ["Action", "Adventure", "Sci-Fi"]
    assert media.director == ["Christopher Nolan"]
