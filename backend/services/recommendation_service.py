from threading import Thread, Lock
import backend.app
from backend.app import db
import math
import numpy as np
import time
import traceback

from pathlib import Path
import joblib

from werkzeug.exceptions import HTTPException
from flask import jsonify, request


from backend.database.db_connection import get_db_connection
from backend.models.movie_model import (WatchedMovie, Rating)
from backend.models.content_based import get_similar_movies
from backend.services.movie_service import safe_number
from backend.utils.auth_utils import ( get_current_user )
from backend.training.train_svd import retrain_model
from backend.recommender.model_store import reload_svd_model, get_model, get_movie_embeddings, get_movie_map, get_reverse_movie_map, get_user_map

# BASE_DIR = Path(__file__).resolve().parent.parent

model = None
movie_embeddings = None
movie_map = None
user_map = None
reverse_movie_map = None

hugging_repo="JonBuwembo/movie-recommender-models"

retrain_lock = Lock()
is_retraining = False

# prevent race conditions when many users are using the app and
# model needs retraining for users.
def trigger_retrain():
    global is_retraining

    if is_retraining:
        return

    is_retraining = True

    try:
        retrain_model()
    finally:
        is_retraining = False

def get_recommendations_service():

    """
    Collaberative Filtering
    """

    global movie_embeddings, movie_map, user_map

    print(">>> Entered get_recommendations_service")

    try:
        user_id = get_current_user(request)

        if not user_id:
            return jsonify({
                "message" : "Unauthorized"
            }), 401

        limit = int(request.args.get("limit", 12))
        ratings = Rating.query.filter_by(user_id=user_id).all()
        rating_count = len(ratings)

        if rating_count == 0:
            return get_popular_movies(limit)
        elif rating_count < 5:
            return get_content_based_recommendation(limit)
        elif rating_count % 5 == 0:
            print("retraining")
            trigger_retrain() 

            print("We are here in recommendations")
    
        model = get_model()
        user_map = get_user_map()
        movie_map = get_movie_map()
        movie_embeddings = get_movie_embeddings()
        reverse_movie_map = get_reverse_movie_map()

        print("Current user:", user_id)
        print("User map contains:", len(user_map), "users")
        print("User exists?", user_id in user_map)
        
        if user_id not in user_map:
            return jsonify({"Error" : "User not in user map"}), 404
            

        # extract user index for matrix.
        user_idx = user_map[user_id]

        # fetch all user interactions, what user already saw
        watched = WatchedMovie.query.filter_by(user_id=user_id).all()
        rated = Rating.query.filter_by(user_id=user_id).all()

        watched_movie_ids = {
            movie.movie_id
            for movie in watched
        }

        rated_movie_ids = {
            movie.movie_id
            for movie in rated
        }

        excluded_movies =  watched_movie_ids | rated_movie_ids

        user_vector = np.zeros(movie_embeddings.shape[1])
        user_ratings = Rating.query.filter_by(
            user_id=user_id
        ).all()


        # higher ratings influence taste more so we multiply each latent factor for a particular movie by its rating.
        for rating in user_ratings:
            if rating.movie_id not in movie_map:
                continue

            movie_idx = movie_map[rating.movie_id]

            movie_vector = (
                movie_embeddings[movie_idx]
            )

            user_vector += ( movie_vector * rating.rating)

        scores = []

        for movie_idx, movie_vector in enumerate(movie_embeddings):
            movie_id = reverse_movie_map[movie_idx]

            if movie_id in excluded_movies:
                continue

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
        recommendations = []


        top_movies = scores[:limit]

        movie_ids = [int(movie["movie_id"]) for movie in top_movies]
        movie_lookup = get_movie_lookup(movie_ids)

        for movie in top_movies:
            movie_id = int(movie["movie_id"])
            movie_info = movie_lookup.get(movie_id, {})

            recommendations.append({
                "movie_id": movie_id,
                **movie_info
            })

        recommended_information = {
            "message" : "Successfully retrieved collaborative recommendations! ",
            "recommendations" : recommendations
        }

        return jsonify(recommended_information)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({"error" : f"ERROR --> {e}"})
        raise

def get_content_based_recommendation(limit):

    """ 
    Recommend movies similar to the movies the user already rated.
    Higher rated movies represent stronger user preferences.
    Uses Position-Based Decay where a decay fynction ensures closer neighbors recieve larger scores.
    Movies with multiple user preferences (in more than one KNN list) gets rewarded higher.
    """

    try:

        print("In content based recommendations....")

        # get the movies the user rated
        user_id  = get_current_user(request)
        ratings = Rating.query.filter_by(user_id=user_id).all()
        movie_ids = [rating.movie_id for rating in ratings]

        scores = {}
        watched = set()

        for r in ratings:
            movie_id = r.movie_id
            rating_weight = r.rating

            watched.add(movie_id)

            similar_movies = get_similar_movies(movie_id)

            # Decay weight based on position in KNN
            for i, mid in enumerate(similar_movies):

                # skip movies that are watched already (dont recommend movies they already saw)
                if mid in watched:
                    continue

                # Ensures top KNN matter more. Decay function
                weight = rating_weight * (1 / (i + 1))

                # Preference strength: higher rated movies matter more.
                # scores that appear in multiple movies get rewarded by score accumulation.
                scores[mid] = (weight + scores.get(mid, 0))

        top_movies = sorted(
            scores.items(), # scores converted into tuple (movie_id, score)
            key=lambda x: x[1], # sorted by score
            reverse=True
        )

        # get a certain number of movie_ids (the limit)
        movie_ids = [movie_id for movie_id, _ in top_movies[:limit]]

        # look up those movies
        movie_lookup = get_movie_lookup(movie_ids)
        recommendations = []

        for movie_id in movie_ids:
            movie_info = movie_lookup.get(movie_id, {})
            recommendations.append(movie_info)

        return jsonify({
            "message" : "Successfully retrieved content based recommendations based on less than 5 ratings",
            "recommendations" : recommendations
        })

    except Exception as e:
        print(f"Error with content based recommendations: {e}")
        return jsonify({"error" : "Unable to fetch content based recommendations"})


def get_popular_movies(limit):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT
            movie_id,
            AVG(rating) As avg_rating,
            COUNT(*) AS vote_count
        FROM ratings
        GROUP BY movie_id
        HAVING COUNT(*) >= 1
        ORDER BY avg_rating DESC, vote_count DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        movie_ids = [row["movie_id"] for row in results]
        movie_lookup = get_movie_lookup(movie_ids)

        movies = []

        for movie in results:
            movie_id = int(movie["movie_id"])
            movie_info = movie_lookup.get(movie_id, {})
            
            movies.append({
                "movie_id" : movie_id,
                **movie_info
            })

        recommended_information = {
            "message" : "Successfully retrieved collaborative recommendations! ",
            "recommendations" : movies[:limit]
        }

        return jsonify(recommended_information)

    except Exception as e:
        print(f"Error, unable to retrieve popular movies: {e}")
        return jsonify({"error" : f"Unable to retrieve popular movies {e}"})
    finally:
        if connection:
            connection.close()
        if cursor:
            cursor.close()

def get_rating_metrics_service(movie_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT
            AVG(rating) AS avg_rating,
            COUNT(*) AS vote_count
        FROM ratings
        WHERE movie_id = %s
        GROUP BY movie_id
        """

        cursor.execute(query, (movie_id,))
        results = cursor.fetchone()

        if results is None:
            return jsonify({
                "avg_rating" : 0,
                "vote_count" : 0
            })

        return jsonify({
            "avg_rating" : results["avg_rating"],
            "vote_count" : results["vote_count"]
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return jsonify({"error" : "metrics for rating have failed to be captured"})
    finally:
        connection.close()
        cursor.close()


def get_movie_lookup(movie_ids):

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
            WHERE m.movie_id = ANY(%s)
            GROUP BY 
                m.movie_id, 
                m.title, 
                m.overview, 
                m.release_year, 
                m.rating_avg, 
                m.poster_url
            
            ORDER BY m.movie_id
            
        """

        cursor.execute(query, (movie_ids,))
        rows = cursor.fetchall()

        movie_lookup = {
            int(row["movie_id"]): 
            {
                "movie_id": row["movie_id"],
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
        user_id = get_current_user(request=request)

        if not user_id:
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
        WHERE 
            wm.user_id = %s
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

        cursor.execute(query, (user_id,))
        movie = cursor.fetchone()

        # new users
        if movie is None:
            return jsonify({
                "movie_title": None,
                "recs": [],
                "message": "User has not watched any movies yet."
            })

        rec_movie_ids = get_similar_movies(movie["movie_id"], 10, offset=0)
        
        movie_lookup = get_movie_lookup(rec_movie_ids)
        movies = []

        for movie_id in movie_lookup:
            movie_info = movie_lookup.get(movie_id, {})
            movies.append(movie_info)

        return jsonify({
            "movie_title": movie["title"],
            "recs" : movies
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
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
    