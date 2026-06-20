import pickle
import os
from database.db_connection import get_db_connection
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

NN_MODEL_PATH = os.path.join(BASE_DIR, 'artifacts', 'nearest_neighbors_model.pkl')
TFIDF_PATH = os.path.join(BASE_DIR, 'artifacts', 'tfidf_matrix.pkl')
MOVIES_DF_PATH = os.path.join(BASE_DIR, 'artifacts', 'movies_df.pkl')

tfidf_matrix = None
nn_model = None
movies_df = None
movie_id_to_index = None

def load_artifacts():
    global tfidf_matrix, nn_model, movies_df, movie_id_to_index
    with open(TFIDF_PATH, 'rb') as f:
        tfidf_matrix = pickle.load(f)

    with open(NN_MODEL_PATH, 'rb') as f:
        nn_model = pickle.load(f)

    with open(MOVIES_DF_PATH, 'rb') as f:
        movies_df = pickle.load(f)

    movie_id_to_index = {
        row["movie_id"]: idx
        for idx, row in movies_df.iterrows()
    }

def get_similar_movies(movie_id, top_n=10, offset=0):
    global ifidf_matrix, nn_model, movies_df

    if tfidf_matrix is None:
        load_artifacts()
        
    movie_index = movie_id_to_index.get(movie_id)

    if movie_index is None:
        return []

    distances, indices = nn_model.kneighbors(
        tfidf_matrix[movie_index],
        n_neighbors = top_n + offset + 1
    )

    similar_indices = indices.flatten()[1 + offset : top_n + offset + 1]

    # iloc: integer-location based indexing for selection by position
    return movies_df.iloc[similar_indices][[
        'movie_id', 
        'title', 
        'overview', 
        'genres', 
        'release_year', 
        'rating_avg', 
        'poster_url'
    ]].to_dict(orient='records')