# Main API server
# endpoints go here directly. you only have two: GET /movies and GET /recommendation/:movieId

from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import get_db_connection

load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/api/movies', methods=['GET'])
def get_all_movies():
    # pull data from dbeaver
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        if not conn:
           return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        query = """
        SELECT 
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
        """

        cursor.execute(query)
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

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Failed to fetch movies"}), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify(movies)

@app.route('/api/movies/<genre>', methods=['GET'])
def get_movies_by_genre(genre):
    
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        query = """
        SELECT 
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
        WHERE g.name = %s;
        """

        cursor.execute(query, (genre,))
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

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Failed to fetch movies by genre"}), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify(movies)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)