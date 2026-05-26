from flask import Blueprint, jsonify
from services.movie_service import (
    get_all_movies_service,
    get_movies_by_genre_service,
    get_movie_details_service,
    get_watchlist_service,
    add_to_watchlist_service,
    remove_from_watchlist_service,
    handle_rating_service
)

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/api/movies', methods=['GET'])
def get_all_movies():
    return get_all_movies_service()

@movies_bp.route('/api/movies/<genre>', methods=['GET'])
def get_movies_by_genre(genre):
    return get_movies_by_genre_service(genre)

@movies_bp.route('/api/details/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    return get_movie_details_service(movie_id)

@movies_bp.route('/api/watchlist/<int:user_id>', methods=['GET'])
def get_user_watchlist(user_id):
    return get_watchlist_service(user_id)

@movies_bp.route('/api/watchlist/<int:user_id>', methods=['POST'])
def add_to_watchlist(user_id):
    return add_to_watchlist_service(user_id)

@movies_bp.route('/api/watchlist/<int:user_id>/<int:movie_id>', methods=['DELETE'])
def remove_from_watchlist(user_id, movie_id):
    return remove_from_watchlist_service(user_id, movie_id)

# add a route for ratings /api/rating/<int:user_id>/<int:movie_id>
@movies_bp.route('/api/rating', methods=['POST'])
def handle_rating():
    return handle_rating_service()