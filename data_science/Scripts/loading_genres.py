import os
import time
import requests
import sys

from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent / ".env"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
backend_path = BASE_DIR / "backend"
models_path = backend_path / "models"

load_dotenv(dotenv_path=dotenv_path)
sys.path.append(str(backend_path))

from database.db_connection import get_db_connection

GENRE_NAME_MAP = {
    "Science Fiction": "Sci-Fi",
    "Family": "Children's",
    "Crime": "Crime",
    "Fantasy": "Fantasy",
    "War": "War",
    "Animation": "Animation",
    "Western": "Western",
    "Drama": "Drama",
    "Action": "Action",
    "Horror": "Horror",
    "Mystery": "Mystery",
    "Comedy": "Comedy",
    "Romance": "Romance",
    "Music": "Musical",
    "Adventure": "Adventure",
    "Documentary": "Documentary",
    "Thriller": "Thriller"
}

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise RuntimeError("Missing TMDB_TOKEN from .env")

# HEADERS = {
#     "Authorization" : f"bearer {TMDB_TOKEN}",
#     "accept" : "application/json"
# }

BASE_URL = "https://api.themoviedb.org/3"

def tmdb_get(path, params=None, retries=3):
    if params is None:
        params = {}

    params["api_key"] = TMDB_API_KEY
    url = f"{BASE_URL}{path}"

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=(5, 10)  # 5 sec connect, 10 sec read
            )

            if response.status_code == 429:
                print("Rate limited. Sleeping 10 seconds...", flush=True)
                time.sleep(10)
                continue

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print(f"TMDB timeout on attempt {attempt}/{retries}. Skipping soon...", flush=True)
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"TMDB request error on attempt {attempt}/{retries}: {e}", flush=True)
            time.sleep(2)

def load_tmdb_genres():
    data = tmdb_get("/genre/movie/list", {"language": "en-US"})
    return {genre["id"] : genre["name"] for genre in data["genres"]}

def search_movies(title, release_year):
    params = {
        "query" : title,
        "include_adult" : "false",
        "language": "en-US",
        "page": 1
    }

    if release_year:
        params["primary_release_year"] = str(int(float(release_year)))
    
    data = tmdb_get("/search/movie", params)

    if not data:
        print(f"Skipping {title}: TMDB request failed or timed out", flush=True)
        return None

    results = data.get("results", [])

    if not results:
        return None
    
    return results[0]

def ensure_genre(cursor, genre_name):
    cursor.execute(
        """
        INSERT INTO genres (name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING 
        RETURNING genre_id;
        """,
        (genre_name,)
    )

    row = cursor.fetchone()

    if row: 
        return row["genre_id"] if isinstance(row, dict) else row[0]

    cursor.execute(
        "SELECT genre_id FROM genres WHERE name = %s;", (genre_name,)
    )

    row = cursor.fetchone()
    return row["genre_id"] if isinstance(row, dict) else row[0]


def main(limit=75000):
    connection = get_db_connection()
    cursor = connection.cursor()

    tmdb_genres = load_tmdb_genres()

    cursor.execute(
        """
        SELECT m.movie_id, m.title, m.release_year
        FROM movies m
        LEFT JOIN "MovieGenres" mg ON m.movie_id = mg.movie_id
        WHERE mg.movie_id IS NULL
            AND m.title IS NOT NULL
            AND TRIM(m.title) <> ''
        ORDER BY m.movie_id
        LIMIT %s;
        """,
        (limit,)
    )

    movies = cursor.fetchall()

    print(f"Found {len(movies)} movies missing genres.")

    matched = 0

    for movie in movies:
        movie_id = movie["movie_id"]
        title = movie["title"]
        release_year = movie["release_year"]

        try:
            print(f"Searching TMDB for: {title} ({release_year})", flush=True)
            result = search_movies(title, release_year)

            if not result:
                print(f"No TMDB match: {title} ({release_year})")
                continue

            genre_ids = result.get("genre_ids", [])

            if not genre_ids:
                print(f"No genres found for {title}")
                continue

            for tmdb_genre_id in genre_ids:
                genre_name = tmdb_genres.get(tmdb_genre_id)
                db_name = GENRE_NAME_MAP.get(genre_name)


                if not db_name:
                    continue

                cursor.execute(
                    "SELECT genre_id FROM genres WHERE name = %s",
                    (db_name,)
                )

                row = cursor.fetchone()

                if not row:
                    print(f"Genre not found in database genres table: {db_name}")
                    continue

                db_genre_id = row["genre_id"]


                cursor.execute(
                    """
                    INSERT INTO "MovieGenres" (movie_id, genre_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (movie_id, db_genre_id)
                )
            
            matched += 1
            print(f"Added genres for {title}: {[tmdb_genres[g] for g in genre_ids if g in tmdb_genres]}")

            if matched % 100 == 0:
                connection.commit()
                print("---------------------------------------------------------------------")
                print(f"********Saving progress for 100 movies! Successfully matched {matched} movies so far!**********")
                print("---------------------------------------------------------------------")

            time.sleep(1.25)

        except Exception as e:
            print(f"Error on {title}: {e}")
            connection.rollback()
            continue

    cursor.close()
    connection.commit()
    connection.close()
    

    print(f"Finished! Successfully matched {matched}/{len(movies)} movies!")


if __name__ == "__main__":
    main(limit=75000)
