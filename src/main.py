from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv('OMDb_API_KEY')

# TODO: add CLI param change
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
for k, v in movie_info.items():
    print(k,": ", v)
