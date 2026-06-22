from database.db_connection import get_db_connection
from models.content_based import get_similar_movies
from werkzeug.exceptions import HTTPException
from huggingface_hub import hf_hub_download
from flask import jsonify, request
import app
from app import db
import math
import numpy as np
import time

from pathlib import Path
import joblib

from models.movie_model import (WatchedMovie, Rating)
from services.movie_service import safe_number
from utils.auth_utils import ( get_current_user )

BASE_DIR = Path(__file__).resolve().parent.parent

model = None
movie_embeddings = None
movie_map = None
user_map = None
reverse_movie_map = None

def load_svd_artifacts():
    global model, movie_embeddings, movie_map, user_map, reverse_movie_map

    if model is not None:
        return

    model_path = hf_hub_download(
        repo_id="JonBuwembo/movie-recommender-models",
        filename="svd.pkl"
    )

    movie_path = hf_hub_download(
        repo_id="JonBuwembo/movie-recommender-models",
        filename="movie_map.pkl"
    )
    user_path = hf_hub_download(
        repo_id="JonBuwembo/movie-recommender-models",
        filename="user_map.pkl"
    )

    model_data = joblib.load(model_path)
    movie_map = joblib.load(movie_path)
    user_map = joblib.load(user_path)

    model = model_data["model"]
    movie_embeddings = model_data["movie_embeddings"]

    reverse_movie_map = {
        col_id : movie_id
        for movie_id, col_id
        in movie_map.items()
    }

def get_recommendations():
    global movie_embeddings, movie_map, user_map

    if movie_embeddings is None:
        load_svd_artifacts()

    user_id = get_current_user(request)
    limit = int(request.args.get("limit", 18))


    if not user_id:
        return jsonify({
            "message": "Unauthorized"
        }), 401
    
    if user_id not in user_map:
        return jsonify({
            "message": "No recommendation profile for user"
        }), 404

    # extract user index for matrix.
    user_idx = user_map[user_id]

    # fetch all user interactions, what user already saw
    watched = WatchedMovie.query.filter_by(user_id=user_id).all()
    rated = Rating.query.filter_by(user_id=user_id).all()

    # creates sets, fast lookup: {550, 991, 122, ...}
    watched_movie_ids = {
        movie.movie_id
        for movie in watched
    }

    rated_movie_ids = {
        movie.movie_id
        for movie in rated
    }

    excluded_movies =  watched_movie_ids | rated_movie_ids

    # embeddings are: 300k movies * certain number of latent factors per movie
    # extract those latent factors for each movie (user's tastes)
    user_vector = np.zeros(movie_embeddings.shape[1])
    user_ratings = Rating.query.filter_by(
        user_id=user_id
    ).all()


    # higher ratings influence taste more so we multiply each latent factor for a particular movie by its rating.
    for rating in user_ratings:
        if rating.movie_id not in movie_map:
            continue

        movie_idx = movie_map[rating.movie_id]

        # print(model_data["movie_embeddings"].shape)
        # print(len(movie_map))
        # print(movie_map)


        movie_vector = (
            movie_embeddings[movie_idx]
        )

        user_vector += ( movie_vector * rating.rating)

    scores = []

    for movie_idx, movie_vector in enumerate(movie_embeddings):
        movie_id = reverse_movie_map[movie_idx]

        if movie_id in excluded_movies:
            continue

        # heart of recommendation math
        # dot product measures how similar a movie is to user taste.
        # vectors point same direction -> high score
        # vectors point diff direction -> low score
        # returns the highest score.
        score = np.dot(user_vector, movie_vector)

        scores.append({
            "movie_id" : movie_id,
            "score" : float(score)
        })

    # movies ranked best -> worst. ordered by the score.
    scores.sort(
        key= lambda x: x["score"],
        reverse=True
    )

    # we return the top N movies and iterate over each using helper to get info of those movies from db
    movie_lookup = get_movie_lookup()

    recommendations = []


    for movie in scores[:limit]:
        movie_id = int(movie["movie_id"])

        movie_info = movie_lookup.get(movie_id, {})

        recommendations.append({
            "movie_id": movie_id,
            "score" : float(movie["score"]),
            **movie_info
        })

    recommended_information = {
        "message" : "Successfully retrieved collaborative recommendations! ",
        "recommendations" : recommendations
    }

    return recommended_information

def get_rating_metrics_service(movie_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT
            AVG(rating) AS avg_rating,
            COUNT(user_id) AS vote_count
        FROM ratings
        WHERE movie_id = %s
        """

        cursor.execute(query, (movie_id,))
        results = cursor.fetchone()

        return jsonify({
            "avg_rating" : results["avg_rating"],
            "vote_count" : results["vote_count"]
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return jsonify({"error" : "metrics for rating have failed to be captured"})


def get_movie_lookup():

    connection = get_db_connection()
    cursor = connection.cursor()
   
    try:
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
            GROUP BY 
                m.movie_id, 
                m.title, 
                m.overview, 
                m.release_year, 
                m.rating_avg, 
                m.poster_url
            
            ORDER BY m.movie_id
            
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        movie_lookup = {
            int(row["movie_id"]): 
            {
                # "movie_id": int(row["movie_id"]),
                "title": str(row["title"]),
                "overview": str(row["overview"]),
                "release_year": str(row["release_year"]),
                "poster_url": str(row["poster_url"]),
                "genre": str(row["genre"])
            }
            for row in rows
        }

        return movie_lookup
    finally:
        connection.close()
        cursor.close()


def because_you_watched_service():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        user = get_current_user(request=request)

        if not user:
            return jsonify({"Error" : "Cannot identify current user"})

        query = """

        SELECT
            m.movie_id,
            m.title,
            m.overview,
            m.release_year,
            m.poster_url,
            STRING_AGG(g.name, ', ') AS genre
        FROM movies m
        JOIN watched_movies wm 
            ON m.movie_id = wm.movie_id
        JOIN "MovieGenres" mg
            ON m.movie_id = mg.movie_id
        JOIN genres g
            ON mg.genre_id = g.genre_id
        WHERE wm.user_id = %s
        GROUP BY
            m.movie_id,
            m.title,
            m.overview,
            m.release_year,
            m.poster_url,
            wm.watched_at
        ORDER BY
            wm.watched_at DESC
        LIMIT 1;
        """

        cursor.execute(query, (user,))
        movie = cursor.fetchone()

        top_recommendations = get_similar_movies(movie["movie_id"], 10, offset=0)

        for rec in top_recommendations:
            rec['rating_avg'] = safe_number(rec.get('rating_avg'))
            rec['release_year'] = safe_number(rec.get('release_year'))
            if rec['overview'] is None:
                rec['overview'] = "No overview available."

        return jsonify({
            "movie_title": movie["title"],
            "recs" : top_recommendations
        })

    except HTTPException:
        raise
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()
        cursor.close()


# Exclusively for the chatbot
def get_similar_movies_service(movie_id, number_of_movies):

    similar_movies = get_similar_movies(movie_id, number_of_movies, offset=0) 

    for rec in similar_movies:
        rec['rating_avg'] = safe_number(rec.get('rating_avg'))
        rec['release_year'] = safe_number(rec.get('release_year'))
        if rec['overview'] is None:
            rec['overview'] = "No overview available."

    return similar_movies 
    