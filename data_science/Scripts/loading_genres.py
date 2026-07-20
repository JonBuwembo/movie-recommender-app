import os
import time
import requests
import sys
import re

from pathlib import Path
from dotenv import load_dotenv
from rapidfuzz import fuzz

dotenv_path = Path(__file__).parent / ".env"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
backend_path = BASE_DIR / "backend"
models_path = backend_path / "models"

load_dotenv(dotenv_path=dotenv_path)
sys.path.append(str(backend_path))

from database.db_connection import get_db_connection

GENRE_NAME_MAP = {
    "Science Fiction": "Sci-Fi",
    "Family": "Children's and Family",
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
    return None

def load_tmdb_genres():
    data = tmdb_get("/genre/movie/list", {"language": "en-US"})

    if not data:
        raise RuntimeError("Failed to load TMDB genre list.")

    return {genre["id"] : genre["name"] for genre in data["genres"]}

def simplify_title(title):
    return re.split(r'[:\-|]+', title)[0].strip()

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

    # print(f"TMDB returned {len(results)} results")

    best_score = 0
    best_match = None

    if not results and release_year:
        params.pop("primary_release_year", None)
        data = tmdb_get("/search/movie", params)

        if data:
            results = data.get("results", [])

    if not results:
        
        simplified = simplify_title(title)
        # print(f"{simplified}")

        if simplified != title:
            params["query"] = simplified
            data = tmdb_get("/search/movie", params)

            if not data:
                return None

            results = data.get("results", [])

    for movie in results:
        tmdb_title = movie.get("title", "")

        score = fuzz.WRatio(title.lower(), tmdb_title.lower())

        if score > best_score:
            best_score = score
            best_match = movie
    
    # print(f"Movie score {best_score}")
    if best_score < 60:
        return None
    
    return best_match

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

def get_movie_credits(tmdb_movie_id):
    return tmdb_get(f"/movie/{tmdb_movie_id}/credits")

def main(limit=75000):
    connection = get_db_connection()
    cursor = connection.cursor()

    tmdb_genres = load_tmdb_genres()

    cursor.execute(
        """
        SELECT m.movie_id, m.title, m.release_year
        FROM movies m
        INNER JOIN "MovieGenres" mg ON m.movie_id = mg.movie_id
        WHERE TRIM(m.title) <> ''
        AND m.director IS NULL
        ORDER BY m.movie_id
        LIMIT %s;
        """,
        (limit,)
    )

    movies = cursor.fetchall()

    print(f"Found {len(movies)} movies missing genres.")

    matched = 0
    not_matched = 0
    processed = 0

    
    for movie in movies:

        processed += 1

        movie_id = movie["movie_id"]
        title = movie["title"]
        release_year = movie["release_year"]

        try:
            print(f"Searching TMDB for: {title} ({release_year})", flush=True)
            result = search_movies(title, release_year)

            if not result:
                print(f"No TMDB match: {title} ({release_year})")
                not_matched += 1
                continue

            genre_ids = result.get("genre_ids", [])

            tmdb_movie_id = result["id"]

            credits = get_movie_credits(tmdb_movie_id)

            if credits:
                cast = credits.get("cast", [])
                crew = credits.get("crew", [])

                if cast:
                    for idx, actor in enumerate(cast[:5]):
                        actor_name = actor["name"]
                        cursor.execute(
                            """
                            INSERT INTO moviecast (movie_id, actor, cast_order)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING
                            """,
                            (movie_id, actor_name, idx)
                        )
                    print(f"Cast found for {title}")
                else:
                    print(f"No cast was found for {title}.")


                if crew:
                    director = None
                    for member in crew:
                        if member["job"] == "Director":
                            director = member["name"]
                            break
                    
                    if director:
                        cursor.execute(
                            """ 
                            UPDATE movies 
                            SET directors = %s
                            WHERE movie_id = %s
                            """,
                            (director, movie_id)
                        )
                        

                        print(f"Director found for {title}: {director}")
                else:
                    print(f"No director found for {title}")
            else:
                print(f"credits not found for {title}.")


            # cursor.execute("SELECT genre_id FROM genres WHERE name = %s", ("Other",))
            # other_genre_id = cursor.fetchone()["genre_id"] # get the id of that entry

            # if not genre_ids:

            #     # add this movie to other category
            #     cursor.execute(
            #         """
            #         INSERT INTO "MovieGenres" (movie_id, genre_id)
            #         VALUES (%s, %s)
            #         ON CONFLICT DO NOTHING;
            #         """,
            #         (movie_id, other_genre_id)
            #     )
            #     print(f"Rows inserted: {cursor.rowcount}")

            #     print(f"Movie was found but No genres found for {title}, added to 'Other' category.")

            #     matched += 1

            #     continue

            # for tmdb_genre_id in genre_ids:
            #     genre_name = tmdb_genres.get(tmdb_genre_id)
            #     db_name = GENRE_NAME_MAP.get(genre_name)


            #     if not db_name:
            #         continue

            #     cursor.execute(
            #         "SELECT genre_id FROM genres WHERE name = %s",
            #         (db_name,)
            #     )

            #     row = cursor.fetchone()

            #     if not row:
            #         print(f"Genre not found in database genres table: {db_name}")
            #         continue

            #     db_genre_id = row["genre_id"]


            #     cursor.execute(
            #         """
            #         INSERT INTO "MovieGenres" (movie_id, genre_id)
            #         VALUES (%s, %s)
            #         ON CONFLICT DO NOTHING;
            #         """,
            #         (movie_id, db_genre_id)
            #     )
            #     print(f"Rows inserted: {cursor.rowcount}")
            
            # matched += 1
            # print(f"Added genres for {title}: {[tmdb_genres[g] for g in genre_ids if g in tmdb_genres]}")

            # time.sleep(0.25)

        except Exception as e:
            print(f"Error on {title}: {e}")

            try:
                connection.rollback()
            except Exception:
                print("Rollback failed, database must have disconnected")
            continue
        finally:
            if processed % 100 == 0:
                connection.commit()
                print("---------------------------------------------------------------------")
                print(f"******** Processed: {processed}")
                print(f"********{not_matched} movies were not found so far.")
                print(f"Success Rate: {matched / (processed):.2%}")
                print("---------------------------------------------------------------------")


    try:
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    

    print(f"Finished! Successfully matched {matched}/{len(movies)} movies!")


if __name__ == "__main__":
    main(limit=200000)
