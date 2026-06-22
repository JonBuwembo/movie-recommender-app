from database.db_connection import get_db_connection
from models.content_based import get_similar_movies
from services.recommendation_service import get_movie_lookup
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

        titles = [(row["title"].strip().lower(), row["movie_id"]) for row in rows]
        title_list = [t[0] for t in titles]

        search_query = movie.strip().lower() 

        match = process.extractOne(
            search_query, 
            title_list, 
            scorer=fuzz.ratio, 
            score_cutoff=60
        )

        if not match:
            return jsonify({"top_results": [], "similar_movies": []}), 200 # if no good match, return no results and we can handle that downstream.
        
        matched_title = match[0]
        movie_id = next(m_id for title, m_id in titles if title == matched_title)

        cursor.execute("""
            SELECT 
                m.movie_id,
                m.title,
                m.overview,
                m.release_year,
                m.poster_url,
                STRING_AGG(g.name, ', ') AS genres
            FROM movies m
            LEFT JOIN "MovieGenres" mg ON m.movie_id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.genre_id
            WHERE m.movie_id = %s
            GROUP BY m.movie_id, m.title, m.overview, m.release_year, m.rating_avg, m.poster_url
        """, (movie_id,))

        first_movie = cursor.fetchone()
    
        top_results = get_similar_movies(movie_id, 10, offset=0)
        top_results.insert(0, first_movie) # add the query itself at top of list.

        movie_lookup = get_movie_lookup()
        top_results_list = []

        for movie in top_results:
            movie_info = movie_lookup.get(movie["movie_id"], {})
            top_results_list.append(movie_info)

        similar_movies = get_similar_movies(movie_id, 30, offset=10)
        similar_movies_list = []

        for movie in similar_movies:
            movie_info = movie_lookup.get(movie["movie_id"], {})
            similar_movies_list.append(movie_info)

        print(top_results_list[0])
        
        response = {
            "top_results": top_results_list,
            "similar_movies": similar_movies_list
        }

        return jsonify(response), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Failed to search movies"}), 500
    finally:
        conn.close()
        cursor.close()