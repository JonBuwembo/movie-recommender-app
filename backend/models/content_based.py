import pickle
import os
from database.db_connection import get_db_connection
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from huggingface_hub import hf_hub_download, login, upload_file

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

neighbor_matrix = None
movie_id_to_index = None

hugging_repo="JonBuwembo/movie-recommender-models"

def load_artifacts():
    global neighbor_matrix, movie_id_to_index

    # prevents files from being downloaded again.
    if (
        neighbor_matrix is not None
        and movie_id_to_index is not None
    ):
        return
    
    NEIGHBOR_MATRIX_PATH = hf_hub_download(
        repo_id=hugging_repo,
        filename="neighbor_matrix.pkl"
    )

    MOVIE_ID_TO_INDEX_PATH = hf_hub_download(
        repo_id=hugging_repo,
        filename='movie_id_to_index.pkl'
    )

    with open(NEIGHBOR_MATRIX_PATH, 'rb') as f:
        neighbor_matrix = pickle.load(f)

    with open(MOVIE_ID_TO_INDEX_PATH, "rb") as f:
        movie_id_to_index = pickle.load(f)


def get_similar_movies(movie_id, top_n=10, offset=0):
    global neighbor_matrix, movie_id_to_index

    if neighbor_matrix is None:
        load_artifacts()
        
    movie_index = movie_id_to_index[movie_id]

    if movie_index is None:
        return []

    movie_ids = neighbor_matrix[movie_index]
    similar_movie_ids = movie_ids[1 + offset : top_n + offset + 1]

    return [int(movie_id) for movie_id in similar_movie_ids]
    