import requests
import os
from dotenv import load_dotenv
from extensions import db
from models import Movie
from app import app  # Import app to use the DB connection
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')

def fetch_tmdb_movies():
    page = 1
    total_pages = 500
    all_movies = []

    while page <= total_pages:
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}'
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error fetching data from TMDB on page {page}: {response.status_code}")
            break

        movies = response.json().get('results', [])
        if not movies:
            print(f"No movies found on page {page}")
        else:
            print(f"Fetched {len(movies)} movies from page {page}")
            all_movies.extend(movies)

        page += 1

    return all_movies

def insert_movies_into_db(movies):
    with app.app_context():
        if not movies:
            print("No movies to insert.")
            return

        print(f"Inserting or updating {len(movies)} movies into the database...")
        for movie in movies:
            # Check if movie with the same title already exists
            existing_movie = Movie.query.filter_by(title=movie['title']).first()

            if existing_movie:
                print(f"Movie '{movie['title']}' already exists. Skipping...")
                continue

            try:
                # Create a new movie record
                new_movie = Movie(
                    title=movie['title'],
                    overview=movie.get('overview', ''),
                    release_date=movie.get('release_date', ''),
                    poster_path=movie.get('poster_path', ''),
                    vote_average=movie.get('vote_average', None)
                )
                db.session.add(new_movie)
            except Exception as e:
                print(f"Error inserting movie '{movie['title']}': {str(e)}")

        try:
            db.session.commit()
            print(f"{len(movies)} movies inserted or updated into the database.")
        except Exception as e:
            print(f"Error committing transaction: {str(e)}")
            db.session.rollback()


if __name__ == "__main__":
    movies = fetch_tmdb_movies()
    insert_movies_into_db(movies)
