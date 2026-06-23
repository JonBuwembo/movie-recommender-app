import pickle
import os
from database.db_connection import get_db_connection
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from huggingface_hub import hf_hub_download, login, upload_file

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

nn_model = None
movie_id_to_index = None
index_to_movie_id = None

hugging_repo="JonBuwembo/movie-recommender-models"

def load_artifacts():
    global tfidf_matrix, nn_model, movies_df, movie_id_to_index, index_to_movie_id

    # prevents files from being downloaded again.
    if (
        nn_model is not None
        and index_to_movie_id is not None
        and movie_id_to_index is not None
    ):
        return
    
    NN_MODEL_PATH = hf_hub_download(
        repo_id=hugging_repo,
        filename="nearest_neighbors_model.pkl"
    )

    MOVIE_ID_TO_INDEX_PATH = hf_hub_download(
        repo_id=hugging_repo,
        filename='movie_id_to_index.pkl'
    )
    INDEX_TO_MOVIE_ID_PATH = hf_hub_download(
        repo_id=hugging_repo,
        filename='index_to_movie_id.pkl'
    )

    with open(NN_MODEL_PATH, 'rb') as f:
        nn_model = pickle.load(f)

    with open(MOVIE_ID_TO_INDEX_PATH, "rb") as f:
        movie_id_to_index = pickle.load(f)

    with open(INDEX_TO_MOVIE_ID_PATH, "rb") as f:
        index_to_movie_id = pickle.load(f)

    print("movie_id_to_index is None:", movie_id_to_index is None)
    print("index_to_movie_id is None:", index_to_movie_id is None)


def get_similar_movies(movie_id, top_n=10, offset=0):
    global tfidf_matrix, nn_model, movie_id_to_index, index_to_movie_id

    if nn_model is None:
        load_artifacts()
        
    movie_index = movie_id_to_index[movie_id]

    if movie_index is None:
        return []

    distances, indices = nn_model.kneighbors(
        nn_model._fit_X[movie_index],
        n_neighbors = top_n + offset + 1
    )

    similar_indices = indices.flatten()[1 + offset : top_n + offset + 1]


    return [
        {"movie_id" : index_to_movie_id[index]}
        for index in similar_indices
    ]