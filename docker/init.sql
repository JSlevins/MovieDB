BEGIN;

-- TYPES
CREATE TABLE types (
    type_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- INSERTING default types
INSERT INTO types (type_id, name)
VALUES (1, 'movie'), (2, 'series');

CREATE TABLE statuses (
    status_id INT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- INSERTING default status
INSERT INTO statuses (status_id, name)
VALUES (1, 'watched');

-- TITLES
CREATE TABLE titles (
    title_id SERIAL PRIMARY KEY,
    title VARCHAR(150) unique not null,
    year INT NOT NULL,
    runtime TEXT,
    poster TEXT,
    plot TEXT,
    awards TEXT,
    imdb_rating NUMERIC(3,1) not null,
    imdbID VARCHAR(15) unique not null,
    type_id INT REFERENCES types(type_id),
    my_rating INT, -- my own rating (0, 10)
    -- For future functionality implementation - not used at this moment (But 1 means 'watched')
    status_id INT REFERENCES statuses(status_id) DEFAULT 1
);

-- PEOPLE
CREATE TABLE people (
    person_id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

-- TYPE > role_type
CREATE TYPE role_type AS ENUM ('actor', 'director', 'writer', 'creator'); -- roles

-- TITLE_ROLES
CREATE TABLE title_roles (
    title_id INT REFERENCES titles(title_id),
    person_id INT REFERENCES people(person_id),
    role role_type not null,

    PRIMARY KEY (title_id, person_id, role)
);

-- GENRES
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- TITLE_GENRES
CREATE TABLE title_genres (
    title_id INT REFERENCES titles(title_id),
    genre_id INT REFERENCES genres(genre_id),

    PRIMARY KEY (title_id, genre_id)
);

-- COUNTRIES
CREATE TABLE countries (
    country_id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

-- TITLE_COUNTRIES
CREATE TABLE title_countries (
    title_id INT REFERENCES titles(title_id),
    country_id INT REFERENCES countries(country_id),

    PRIMARY KEY (title_id, country_id)
);


COMMIT;
