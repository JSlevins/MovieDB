#!/bin/bash

set -e 

DB_SERVICE="moviedb_db"
APP_SERVICE="moviedb_app"


# Function to stop containers on ctrl+c or `kill`
cleanup() {
    echo ""
    echo "Stopping services..."
    docker-compose down
    echo ""
    echo "Have a nice day!"
    exit
}

# Catch interrupt signals
trap cleanup SIGINT SIGTERM 

echo "Starting PostgreSQL..."
docker-compose up -d db

echo "Waiting for PostgreSQL to be ready..."
until docker exec $DB_SERVICE pg_isready -U admin -d moviedb > /dev/null  2>&1; do
    sleep 1
done
echo "PostgreSQL is ready."

echo "Starting MovieDb Client..."
docker-compose up -d app
docker exec -it $APP_SERVICE  python -u src/main.py

# On finish
cleanup
