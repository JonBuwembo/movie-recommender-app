# To Run file, run:  python -m models.rebuilt_sim_matrix_script from backend/ folder

import os
import pickle
import pandas as pd
import numpy as np

from backend.database.db_connection import get_db_connection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from huggingface_hub import upload_file, login
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)
load_dotenv()

hugging_face_key = os.getenv("HUGGINGFACE_API_KEY")

if hugging_face_key is None:
    raise ValueError("Hugging Face Key in .env cannot be read or is not found!")

hugging_repo = "JonBuwembo/movie-recommender-models"
login(hugging_face_key)

MOVIE_ID_TO_INDEX_PATH = os.path.join(ARTIFACTS_DIR, "movie_id_to_index.pkl")
NEIGHBOR_MATRIX_PATH = os.path.join(ARTIFACTS_DIR, "neighbor_matrix.pkl")


"""
    Numpy --> Builds the empty matrix that will be later populated with KNN similar movies per movie.
    Scikit-Learn --> Tfidf Vectorization (feature extraction) and Nearest Neighbor ML model
    huggingface --> hosts our large ML files to prevent memory overload.
"""


def upload_artifacts():
    """
    Pushing updated model files to Hugging Face
    """

    upload_file(
        path_or_fileobj=NEIGHBOR_MATRIX_PATH,
        path_in_repo="neighbor_matrix.pkl",
        repo_id=hugging_repo,
        repo_type="model"
    )

    upload_file(
        path_or_fileobj=MOVIE_ID_TO_INDEX_PATH,
        path_in_repo="movie_id_to_index.pkl",
        repo_id=hugging_repo,
        repo_type="model"
    )

def build_movie_metadata_model():
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    SELECT 
        m.movie_id, 
        m.title, 
        COALESCE(m.overview, '') AS overview,
        COALESCE(m.release_year::TEXT, '') AS release_year,
        COALESCE(m.rating_avg::TEXT, '') AS rating_avg,
        COALESCE(m.poster_url, '') AS poster_url, 
        COALESCE(STRING_AGG(g.name, ', '), '') AS genres
    FROM movies m 
    LEFT JOIN "MovieGenres" mg ON m.movie_id = mg.movie_id 
    LEFT JOIN genres g ON mg.genre_id = g.genre_id
    GROUP BY m.movie_id, m.title, m.overview, m.release_year, m.rating_avg, m.poster_url
    ORDER BY m.movie_id;
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    movies_df = pd.DataFrame(rows, columns=columns)
 
    movies_df["text"] = (
        movies_df["title"].fillna("") + " " +
        movies_df["overview"].fillna("") + " " +
        movies_df["genres"].fillna("") + " " +
        movies_df["release_year"].fillna("")
    )

    vectorizer = TfidfVectorizer(
        stop_words="english", 
        max_features=20000,
        min_df=2, # ignore words that appear in fewer than 2 movies
        max_df=0.85 # 
    )

    tfidf_matrix = vectorizer.fit_transform(movies_df["text"])

    # KNN uses cosine similarity ONLY when it needs to find neighbors for a movie.
    # Much better approach than computing a "raw cosine similarity" matrix that compared
    # every movie against every other movie: 250,000 x 250,000 = Billions of comparisons (expensive)
    nn_model = NearestNeighbors(
        metric="cosine",
        algorithm="brute",
        n_neighbors=50
    )

    # KNN finds nearest neighbors on the TF-IDF vectors computed by the vectorizer above.
    # compares vectors of numbers for every movie and checks how similar those numbers are.
    nn_model.fit(tfidf_matrix)

    # Mapping
    movie_id_to_index = {}
    index_to_movie_id = {}

    for idx, row in movies_df.iterrows():
        movie_id = int(row["movie_id"])

        movie_id_to_index[movie_id] = idx
        index_to_movie_id[idx] = movie_id

    neighbor_matrix = np.empty(
        (len(movies_df), 50),
        dtype=np.int32
    )

    distances, indices = nn_model.kneighbors(
        tfidf_matrix,
        n_neighbors=51
    )

    for idx in range(len(movies_df)):
        neighbor_matrix[idx] = [
            index_to_movie_id[i]
            for i in indices[idx][1:]  # skip the first movie (just get its recs)
        ]

    # KNN matrix and movie_id (database) to index mapper saved as PKL files.
    # CACHING --> we lookup movie similarities with this matrix in application.
    with open(NEIGHBOR_MATRIX_PATH, "wb") as f:
        pickle.dump(neighbor_matrix, f)

    with open(MOVIE_ID_TO_INDEX_PATH, "wb") as f:
        pickle.dump(movie_id_to_index, f)

    print(f"Built TF-IDF + nearest neighbor model for {len(movies_df)} movies.")


if __name__ == "__main__":
    build_movie_metadata_model() # Load into artifacts folder
    upload_artifacts() # read from artifacts folder -> upload to hugging face
