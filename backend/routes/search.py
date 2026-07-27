from flask import Blueprint
from backend.services.search_service import search_movies_services
from backend.services.recommendation_service import get_similar_movies_service

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search/<movie>', methods=['GET'])
def search_movies(movie):
    return search_movies_services(movie)


@search_bp.route('/api/search/similar/<movie>', methods=['GET'])
def get_similar_movies(movie, number_of_movies=5):
    return get_similar_movies_service(movie, number_of_movies)

