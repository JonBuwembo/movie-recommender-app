# clean raw data and send it to the processed/ in datasets/

# for queries, use filter in method where you filter out movies with a null overview.abs
# SELECT *
# FROM movies
# WHERE overview IS NOT NULL;

import sys
import os
import pandas as pd

import rapidfuzz
from rapidfuzz import process, fuzz
import unicodedata

import requests
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

# Load environment variables from .env file
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from backend.database.db_connection import get_db_connection

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
BASE_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"


# ============================ helper functions ============================
def normalize_title(title):
    import re
     # Lowercase
    title = title.lower()
    
    # Remove accents
    title = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII')
    
    # Remove leading articles
    title = re.sub(r"^(the|a|an)\s+", "", title)
    
    # Remove trailing articles like ', the', ', a', ', an'
    title = re.sub(r",\s*(the|a|an)$", "", title)
    
    # Remove parentheses and everything inside
    title = re.sub(r"\(.*?\)", "", title)
    
    # Remove punctuation
    title = re.sub(r"[^\w\s]", "", title)

    # Remove leading/trailing whitespace
    title = re.sub(r",\s*(the|a|an)$", "", title, flags=re.IGNORECASE).strip()
    
    # Collapse multiple spaces
    title = re.sub(r"\s+", " ", title)
    
    return title.strip()

def get_best_tmdb_match(movie_title, movie_year, tmdb_results):
    norm_title = normalize_title(movie_title)
    best_score = 0
    best_movie = None

    for tmdb_movie in tmdb_results:
        tmdb_title = tmdb_movie.get("title") or ""
        
        # Normalize TMDb title
        norm_tmdb_title = normalize_title(tmdb_title)

        # Fuzzy match the titles
        score = fuzz.ratio(norm_title, norm_tmdb_title)

        if score > best_score:
            best_score = score
            best_movie = tmdb_movie

    return best_movie if best_score >= 50 else None  


# =========================================== main script ===========================================


connection = get_db_connection()
cursor = connection.cursor()
query ="""
SELECT movie_id, title, overview, release_year, rating_avg, poster_url
FROM movies
WHERE overview IS NULL OR poster_url IS NULL;
"""
cursor.execute(query)

movies = cursor.fetchall()

for movie in movies:
    print(movie)

    # RealDictCursor returns rows as dictionaries, so we can access columns by name
    movie_id = movie["movie_id"]
    title = movie["title"]
    overview = movie["overview"]
    release_year = movie["release_year"]
    rating_avg = movie["rating_avg"]
    poster_url = movie["poster_url"]

    print(f"Processing movie: {title} (ID: {movie_id})")

    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "language": "en-US"
    }

    response = requests.get(BASE_SEARCH_URL, params=params)
    data = response.json()
   
    if data.get("results"):
        tmdb_movie = get_best_tmdb_match(title, release_year, data.get("results", []))

        if not tmdb_movie:
            print(f"No good TMDB match found for '{title}' - skipping.")
            continue

        tmdb_movie_id = tmdb_movie.get("id")
        tmdb_title = tmdb_movie.get("title")
        overview_tmdb = tmdb_movie.get("overview")
        poster_path = tmdb_movie.get("poster_path")
        poster_url_tmdb = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        print(f"TMDB found movie: {tmdb_title} (ID: {tmdb_movie_id})")

        updated = False
        if poster_url is None and poster_url_tmdb is not None:
            cursor.execute(
                "UPDATE movies SET poster_url = %s WHERE movie_id = %s",
                (poster_url_tmdb, movie_id)
            )

        if overview is None and overview_tmdb is not None:
            cursor.execute(
                "UPDATE movies SET overview = %s WHERE movie_id = %s",
                (overview_tmdb, movie_id)
            )
        print("==============================================")
        updated = True

        if updated: 
            print(f"Updated movie '{title}' with poster URL: {poster_url_tmdb} and overview: {overview_tmdb}")
        else:
            print(f"Nothing processed for '{title}'.")

print("Done Processing all movies. Committing changes to the database...")
connection.commit()
connection.close()


