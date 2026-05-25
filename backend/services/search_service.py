from database.db_connection import get_db_connection
from models.content_based import movies_df, get_similar_movies
import math

from flask import jsonify
from rapidfuzz import process, fuzz

import pandas as pd

def safe_number(value, default=0):
    """Return a valid number: replace None or NaN with default."""
    if value is None:
        return default
    try:
        if math.isnan(value):
            return default
    except TypeError:
        # value is not a number, just return default
        return default
    return value



def search_movies_services(movie):
    print(f"Search route hit! movie = {movie}")
    conn = None
    cursor = None

    try:
        conn = get_db_connection()

        cursor = conn.cursor()
        query = """
        SELECT 
            m.movie_id,
            m.title,
            m.overview,
            m.release_year,
            m.rating_avg,
            m.poster_url,
            STRING_AGG(g.name, ', ') AS genre
        FROM movies m
        JOIN "MovieGenres" mg ON m.movie_id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.genre_id
        GROUP BY m.movie_id, m.title, m.overview, m.release_year, m.rating_avg, m.poster_url;
        """
        search_pattern = f"%{movie}%"
        cursor.execute(query, (search_pattern,))
        rows = cursor.fetchall()

        # if not rows:
        #     return jsonify({"top_results": [], "similar_movies": []}), 200
        
        # convert database rows into pandas dataframe for easier manipulation
        # each column is a field name and each row is a movie.
        movies_df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

        titles_series = movies_df['title'].str.strip()
        titles = titles_series.str.lower().tolist() # list of all movie titles in the database, preprocessed to be lowercase and stripped of whitespace for better fuzzy matching.
        search_query = movie.strip().lower() # remove spaces from user input.

        final_query = process.extractOne(search_query, titles, scorer=fuzz.ratio, score_cutoff=60) # returns a tuple of (best matching title, score, index in movies_df)


        if not final_query:
            print(final_query)
            return jsonify({"top_results": [], "similar_movies": []}), 200 # if no good match, return no results and we can handle that downstream.
        
        q_title, q_score, q_index = final_query
        print(f"Best match movies for query is: {q_title} with score of {q_score}") # print for debugging.

        first_movie = movies_df.iloc[q_index].to_dict()
        movie_id = first_movie["movie_id"]
    
        top_results = get_similar_movies(movie_id, 10, offset=0)
        top_results.insert(0, first_movie) # add the query itself at top of list.


        for movie in top_results:
            movie['rating_avg'] = safe_number(movie.get('rating_avg'))
            movie['release_year'] = safe_number(movie.get('release_year'))
            if movie['overview'] is None:
                movie['overview'] = "No overview available."

        similar_movies = get_similar_movies(movie_id, 30, offset=10)

        for movie in similar_movies:
            movie['rating_avg'] = safe_number(movie.get('rating_avg'))
            movie['release_year'] = safe_number(movie.get('release_year'))
            if movie['overview'] is None:
                movie['overview'] = "No overview available."

        # print(f"Top results for search query '{movie}': {[m['title'] for m in top_results]}")
        # print(f"Similar movies for search query '{movie}': {[m['title'] for m in similar_movies]}")

        response = {
            "top_results": top_results,
            "similar_movies": similar_movies
        }

        # print("FINAL RESPONSE:", response)
        return jsonify(response), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Failed to search movies"}), 500
    finally:
        conn.close()
        cursor.close()