from flask import Blueprint
from services.search_service import search_movies_services

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search/<movie>', methods=['GET'])
def search_movies(movie):
    return search_movies_services(movie)