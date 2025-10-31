import re
import os

import requests
from dotenv import load_dotenv

class OMDbError(Exception): pass
class OMDbInvalidKeyError(OMDbError): pass
class OMDbNotFoundError(OMDbError): pass
class OMDbInvalidIDError(OMDbError): pass
class OMDbConnectionError(OMDbError): pass

load_dotenv()
API_KEY = os.getenv('OMDb_API_KEY')

class OMDbClient:
    """
    Handles communication with the OMDb API to search and retrieve movie information.

    Responsibilities:
        - Send search queries to OMDb and return a list of matching movies.
        - Retrieve detailed information for a specific movie by IMDb ID.
        - Handle API keys, request parameters, and basic error checking.
    """
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.base_url = 'https://www.omdbapi.com/'


    def get_title_by_imdbid(self, imdbid: str) -> dict:
        # Format checking
        if not re.fullmatch(r"tt\d{7,9}", imdbid):
            raise ValueError("Invalid IMDb ID format. Expected format: 'tt1234567'")

        # Query parameters
        params = {
            'apikey': self.api_key,
            'i': imdbid,
        }

        return self._request(params)

    def get_title_by_name(self, title: str) -> dict:
        # Query parameters
        params = {
            'apikey': self.api_key,
            't': title,
        }

        return self._request(params)

    def search_title(self, substring: str) -> dict:
        # Query parameters
        params = {
            'apikey': self.api_key,
            's': substring
        }

        return self._request(params)

    def _request(self, params: dict) -> dict:
        # Send request
        response = requests.get(self.base_url, params=params, timeout=10)

        # HTTP status check
        if response.status_code != 200:
            raise OMDbConnectionError(f"OMDb API returned {response.status_code}")
        data = response.json()
        # Response flag check
        return data if data.get('Response') == 'True' else self._handle_error(data)

    def _handle_error(self, data) -> None:
        msg = data.get('Error', 'Unknown error')
        if "Invalid API key!" in msg:
            raise OMDbInvalidKeyError(msg)
        elif "Incorrect IMDb ID." in msg:
            raise OMDbInvalidIDError(msg)
        elif "Movie not found!" in msg:
            raise OMDbNotFoundError(msg)
        else:
            raise OMDbError(msg)
