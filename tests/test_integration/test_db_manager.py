import pytest, json

from src.dbmanager import DbManager
from src.media_title import MediaTitle


@pytest.fixture(scope='module')
def dbm():
    dbm = DbManager(database="moviedb_test", host="db_test", port="5432", user="admin", password="admin")
    dbm.cur.execute("TRUNCATE TABLE titles, people, genres, countries RESTART IDENTITY CASCADE")
    yield dbm
    dbm.conn.close()

def test_db_connection(dbm):
    assert dbm.conn.closed == 0
    dbm.cur.execute("SELECT 1;")
    assert dbm.cur.fetchone() == (1,)

@pytest.fixture(scope="module")
def get_media_title():
    with open ("tests/test_unit/test_movie.json", "r") as file:
        file = json.load(file)
        media = MediaTitle.from_json(file)
    return media

def test_add_title(dbm, get_media_title):
    dbm.add_title(get_media_title, 10)

    dbm.cur.execute("SELECT imdbid FROM titles WHERE title = %s;", ('Inception',))
    assert dbm.cur.fetchone() == ('tt1375666',)

    dbm.cur.execute("SELECT p.name FROM people p JOIN title_roles tr ON p.person_id = tr.person_id WHERE tr.role = %s;", ('actor',))
    query = dbm.cur.fetchall()
    for el in query:
        assert el[0].lower() in[x.lower() for x in ['Leonardo DiCaprio', 'Joseph Gordon-Levitt', 'Elliot Page']]
