from database.db_connection import get_db_connection
from werkzeug.exceptions import HTTPException

from flask import jsonify, request
from models.movie_model import Movie, Watchlist, Rating, WatchedMovie
from models.content_based import get_similar_movies
from datetime import datetime, timezone
from utils.auth_utils import get_current_user
import app
from app import db
import math

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


def get_all_movies_service():
    # pull data from dbeaver
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        if not conn:
           return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        page = int(request.args.get("page", 1))

        limit = int(request.args.get("limit", 48))
        offset = (page - 1) * limit

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

        LIMIT %s OFFSET %s;
        """

        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()

        movies = []
        for row in rows:
            movies.append({
                "movie_id": row["movie_id"],
                "title": row["title"],
                "overview": row["overview"],
                "release_year": row["release_year"],
                "rating_avg" : row["rating_avg"],
                "poster_url" : row["poster_url"] 
            })

        return movies

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {e}")
        return {"error": "Failed to fetch movies"}
    finally:
        cursor.close()
        conn.close()

    

def get_movies_by_genre_service(genre):
    
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit"))

        offset = (page - 1) * limit

        query = """
        SELECT DISTINCT
            m.movie_id,
            m.title,
            m.overview,
            m.release_year,
            m.rating_avg,
            m.poster_url,
            g.name as genre
        FROM movies m
        JOIN "MovieGenres" mg ON m.movie_id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.genre_id
        WHERE g.name = %s
        ORDER BY m.movie_id
        LIMIT %s OFFSET %s;
        """

        cursor.execute(query, (genre, limit, offset))
        rows = cursor.fetchall()

        movies = []
        for row in rows:
            movies.append({
                "movie_id": row["movie_id"],
                "title": row["title"],
                "genre": row["genre"],
                "overview": row["overview"],
                "release_year": row["release_year"],
                "rating_avg" : row["rating_avg"],
                "poster_url" : row["poster_url"] 
            })

        return jsonify(movies), 200

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Failed to fetch movies by genre"}), 500
    finally:
        cursor.close()
        conn.close()



def get_movie_details_service(movie_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
         SELECT 
            m.movie_id,
            m.title,
            m.overview,
            m.release_year,
            m.rating_avg,
            m.poster_url,
            STRING_AGG(g.name, ', ') AS genres
        FROM movies m
        LEFT JOIN "MovieGenres" mg ON m.movie_id = mg.movie_id
        LEFT JOIN genres g ON mg.genre_id = g.genre_id
        WHERE m.movie_id = %s
        GROUP BY m.movie_id, m.title, m.overview, m.release_year, m.rating_avg, m.poster_url;
        """

        cursor.execute(query, (movie_id,))
        row = cursor.fetchone()


        if not row:
            return jsonify({
                "title":  "Unknown Movie",
                "genres": "unknown genre",
                "overview": "Unknown",
                "release_year": 0,
                "rating_avg": 0,
                "poster_url": "Unkown",
                "recommendations": []
            })

        

        movie = {
            "movie_id": row["movie_id"],
            "title": row["title"],
            "genres": row["genres"],
            "overview": row["overview"],
            "release_year": row["release_year"],
            "rating_avg" : row["rating_avg"],
            "poster_url" : row["poster_url"] 
        }

        movie["genres"] = movie["genres"] or "Other"

        top_recommendations = get_similar_movies(movie["movie_id"], 10, offset=0)
        
        for rec in top_recommendations:
            rec['rating_avg'] = safe_number(rec.get('rating_avg'))
            rec['release_year'] = safe_number(rec.get('release_year'))
            if rec['overview'] is None:
                rec['overview'] = "No overview available."

        response = {
            "movie": movie, 
            "recommendations": top_recommendations
        }

        return jsonify(response)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Failed to fetch recommendations"}), 500
    finally:
        connection.close()
        cursor.close()


def get_watchlist_service():
    connection = None
    cursor = None

    user_id = get_current_user(request)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query ="""
            SELECT
                m.movie_id,
                m.title,
                m.overview,
                m.release_year,
                m.rating_avg,
                m.poster_url
            FROM watchlist w 
            JOIN movies m ON w.movie_id = m.movie_id
            WHERE w.user_id = %s
            ORDER BY w.added_at DESC;
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

        movies = []
        for row in rows:
            movies.append({
                "movie_id": row["movie_id"],
                "title": row["title"],
                "overview": row["overview"],
                "release_year": row["release_year"],
                "rating_avg" : row["rating_avg"],
                "poster_url" : row["poster_url"] 
            })

        return jsonify(movies), 200
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Failed to fetch watchlist movies"}), 500
    finally:
        connection.close()
        cursor.close()



def add_to_watchlist_service(movie_id):

    try:
        # access the movies
        # frontend = request.get_json()
        # movie_id = frontend.get("movie_id")
        user_id = get_current_user(request)

        if not movie_id:
            return jsonify({"error":"movie_id is required"}), 400
        
        movie = Movie.query.filter_by(movie_id=movie_id).first()

        if not movie:
            return jsonify({"error" : "This movie cannot be found"}), 404

        # check if this movie is already in the watchlist for this user.
        existing_entry = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()

        if existing_entry:
            return jsonify({"message" : "Movie already exists in watchlist for this user."}), 200
        
        # otherwise
        new_watchlist_entry = Watchlist(user_id=user_id, movie_id=movie_id)
        
        db.session.add(new_watchlist_entry)
        db.session.commit()

        return jsonify({
            "success": "movie added to watchlist!",
            "user_id": user_id,
            "movie_id": movie_id
        }), 201

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred adding to watchlist: {e}")
        return jsonify({"error": f"Failed to add movie to watchlist"})



def remove_from_watchlist_service(movie_id):

    user_id = get_current_user(request)

    try:
        watchlist_entry = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()

        if not watchlist_entry:
            print("Failed to find movie to delete")
            return jsonify({"error" : "movie not in watchlist so can't delete."})
        
        db.session.delete(watchlist_entry)
        db.session.commit()

        return jsonify(
            {
                "message": "successfully removed movie from watchlist",
                "user_id": user_id,
                "movie_id": movie_id
            }
        ), 201
    except HTTPException:
        raise
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred removing from watchlist: {e}")
        return jsonify({"error" : f"Failed to remove movie from watchlist"})
  

def handle_rating_service():
    
    try:
        frontend = request.get_json()

        movie_id = frontend.get("movieId")
        rating = frontend.get("rating")

        user_id = get_current_user(request)
       

        rating_entry = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first() # object

        if rating_entry:
            #  update the movie rating with a new rating and then, update updated_at field, then RETURN
            rating_entry.rating = rating
            rating_entry.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            return jsonify({
                "message" : "rating successfully updated"
            })

        new_rating_entry = Rating(
            user_id=user_id, 
            movie_id=movie_id, 
            rating=rating, 
            rated_at=datetime.now(timezone.utc), 
            updated_at=datetime.now(timezone.utc)) 
        db.session.add(new_rating_entry)
        db.session.commit()

        return jsonify({"message" : "successfully rated movie for a user"})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error" : f"Failed to add rating: {e}" }), 500


def set_watched_service():

    try:
        # get movie_id
        frontend = request.get_json()

        movie_id = frontend.get("movieId")
        # get user_id
        user_id = get_current_user(request)

        movie_status = WatchedMovie.query.filter_by(user_id=user_id, movie_id=movie_id).first()

        if movie_status:
            return jsonify({"message" : "User has already watched this movie! "}), 409

        movie_status = WatchedMovie(user_id=user_id, movie_id=movie_id)
        db.session.add(movie_status)
        db.session.commit()

        return jsonify({"message" : "Success! This movie has been set to watch!"}), 201
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error {e}")
        return jsonify({"error" : f"Failure setting watch status: {e}"})
     

def get_watched_service():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        user_id = get_current_user(request)

        query = """
        SELECT
            m.movie_id,
            m.title,
            m.overview,
            m.release_year,
            m.rating_avg,
            m.poster_url
        FROM watched_movies wm
        JOIN movies m ON wm.movie_id = m.movie_id
        WHERE wm.user_id = %s
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

        movies = []

        for row in rows:

            movie = {
                "movie_id" : row["movie_id"],
                "title" : row["title"],
                "overview": row["overview"],
                "release_year" : row["release_year"],
                "poster_url" : row["poster_url"]
            }

            movies.append(movie)

        return jsonify(movies), 200

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error" : f"Failed to retrieve all watched movies {e}" })
    finally:
        connection.close()
        cursor.close()

def get_rating_service(movie_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        user_id = get_current_user(request)

        query = """
        SELECT
            rating,
            movie_id
        FROM ratings
        WHERE user_id = %s AND movie_id = %s
        """

        cursor.execute(query, (user_id, movie_id))

        rating = cursor.fetchone()

        return jsonify(rating), 201

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error {e}")
        return jsonify({"error" : f"Failed to retrieve rating for this movie {e}"})

