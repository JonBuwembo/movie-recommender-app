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


# building movie index mapping dynamizally from the database
# connection = get_db_connection()
# cursor = connection.cursor()
# query = """
# SELECT 
#     m.movie_id, 
#     m.title, 
#     m.overview, 
#     m.release_year, 
#     m.rating_avg,
#     m.poster_url, 
#     STRING_AGG(g.name, ', ') AS genres
# FROM movies m 
# JOIN "MovieGenres" mg ON m.movie_id = mg.movie_id 
# JOIN genres g ON mg.genre_id = g.genre_id
# GROUP BY m.movie_id, m.title, m.overview, m.release_year, m.rating_avg, m.poster_url;
# """
# cursor.execute(query)

# movies_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])


# movie_indices = {title: idx for idx, title in enumerate(movies_df['title'])}
# movies_df["title_clean"] = movies_df["title"].str.lower().str.strip()
# movie_indices = pd.Series(
#     movies_df.index,
#     index=movies_df['title_clean'].str.lower().str.strip()
#     ).to_dict()


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