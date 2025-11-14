# MovieDB CLI

**MovieDB CLI** is a Python command-line application to search, add, and filter movies using a PostgreSQL database and the OMDb API. 
It supports exporting data to JSON or YAML and includes unit tests.

## Features
- Search movies by title or IMDb ID via OMDb API or local database
- Add new movies to the PostgreSQL database
- Filter movies by rating
- Export movie data to JSON or YAML
- Fully tested with pytest

## Tech Stack
- Python 3.x
- PostgreSQL
- psycopg2
- requests
- dotenv
- pytest
- YAML/JSON handling


## Configuration

## Configuration

Create a `.env` file in the project root with the following variables:
```env
OMDb_API_KEY=<your_omdb_api_key>
DB_USER=<your_database_user>
DB_PASSWORD=<your_database_password>
PYTHONPATH=.
```
Replace placeholders with your actual OMDb API key and PostgreSQL credentials.
Do **not** commit this file to GitHub — add it to `.gitignore`.