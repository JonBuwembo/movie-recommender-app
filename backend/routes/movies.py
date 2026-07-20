from flask import Blueprint, jsonify, request
from services.movie_service import (
    get_all_movies_service,
    get_movies_by_genre_service,
    get_movie_details_service,
    get_watchlist_service,
    add_to_watchlist_service,
    remove_from_watchlist_service,
    handle_rating_service,
    set_watched_service,
    get_watched_service,
    get_rating_service
)

from services.recommendation_service import (
    get_rating_metrics_service,
    get_recommendations_service,
    because_you_watched_service
)

from utils.auth_utils import get_current_user

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/api/movies', methods=['GET'])
def get_all_movies():
    movies = get_all_movies_service()
    return jsonify(movies), 200

@movies_bp.route('/api/movies/<genre>', methods=['GET'])
def get_movies_by_genre(genre):
    return get_movies_by_genre_service(genre)
   

@movies_bp.route('/api/details/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    return get_movie_details_service(movie_id)

@movies_bp.route('/api/watchlist', methods=['GET'])
def get_user_watchlist():
    return get_watchlist_service()

@movies_bp.route('/api/watchlist/<int:movie_id>', methods=['POST'])
def add_to_watchlist(movie_id):
    return add_to_watchlist_service(movie_id)

@movies_bp.route('/api/watchlist/<int:movie_id>', methods=['DELETE'])
def remove_from_watchlist(movie_id):
    return remove_from_watchlist_service(movie_id)

# add a route for ratings /api/rating/<int:user_id>/<int:movie_id>
@movies_bp.route('/api/rating', methods=['POST'])
def handle_rating():
    return handle_rating_service()

@movies_bp.route("/api/recommendations", methods=["GET"])
def recommendations():
    return get_recommendations_service()

@movies_bp.route('/api/rating/<int:movie_id>', methods=['GET'])
def get_rating(movie_id):
    return get_rating_service(movie_id)

@movies_bp.route('/api/watched', methods=['POST'])
def set_watched():
    return set_watched_service()

@movies_bp.route('/api/watched', methods=['GET'])
def get_watched():
    return get_watched_service()

@movies_bp.route('/api/votes/<int:movie_id>', methods=['GET'])
def get_vote_metrics(movie_id):
    return get_rating_metrics_service(movie_id)

@movies_bp.route('/api/because-you-watched', methods=['GET'])
def get_because_you_watched():
    return because_you_watched_service()
