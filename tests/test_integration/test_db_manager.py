import pytest, json

from src.dbmanager import DbManager
from src.media_title import MediaTitle


@pytest.fixture(scope='module')
def dbm():
    # Connecting to Test Db
    dbm = DbManager(database="moviedb_test", host="db_test", port="5432", user="admin", password="admin")
    # Cleaning all tables
    dbm.cur.execute("TRUNCATE TABLE titles, people, genres, countries RESTART IDENTITY CASCADE")
    yield dbm
    # Closing connection
    dbm.conn.close()

def test_db_connection(dbm):
    assert dbm.conn.closed == 0
    dbm.cur.execute("SELECT 1 AS value;")
    assert dbm.cur.fetchone()['value'] == 1

@pytest.fixture(scope="module")
def get_media_title():
    with open ("tests/test_unit/test_movie.json", "r") as file:
        file = json.load(file)
        media = MediaTitle.from_dict(file)
    return media

def test_add_title(dbm, get_media_title):
    dbm.add_title(get_media_title, 10)

    dbm.cur.execute("SELECT imdbid FROM titles WHERE title = %s;", ('Inception',))
    assert dbm.cur.fetchone()['imdbid'] == 'tt1375666'

    dbm.cur.execute("SELECT p.name FROM people p JOIN title_roles tr ON p.person_id = tr.person_id WHERE tr.role = %s;", ('actor',))
    query = dbm.cur.fetchall()
    for el in query:
        assert el['name'].lower() in[x.lower() for x in ['Leonardo DiCaprio', 'Joseph Gordon-Levitt', 'Elliot Page']]
