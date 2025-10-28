from dotenv import load_dotenv
import os
import requests

from src.dbmanager import DbManager
from src.media_title import MediaTitle

load_dotenv()
api_key = os.getenv('OMDb_API_KEY')

def get_movie(title):

    url = 'http://www.omdbapi.com/'
    params = {
        'apikey': api_key,
        't': title,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return f"Error: {response.status_code}"

# Example
movie_info = get_movie("Inception")
movie = MediaTitle.from_json(movie_info)

dbmanager = DbManager()
dbmanager.add_title(movie, 10)