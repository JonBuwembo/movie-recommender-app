# To Run file, run:  python -m models.rebuilt_sim_matrix_script

import os
import pickle
import pandas as pd
from database.db_connection import get_db_connection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

NM_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "nearest_neighbors_model.pkl")
TFIDF_PATH = os.path.join(ARTIFACTS_DIR, "tfidf_matrix.pkl")
VECTORIZER_PATH = os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.pkl")
MOVIES_DF_PATH = os.path.join(ARTIFACTS_DIR, "movies_df.pkl")


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

    # movies_df = pd.read_sql(query, connection)

    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    movies_df = pd.DataFrame(rows, columns=columns)
    # print(movies_df.head())

    movies_df["text"] = (
        movies_df["title"].fillna("") + " " +
        movies_df["overview"].fillna("") + " " +
        movies_df["genres"].fillna("") + " " +
        movies_df["release_year"].fillna("")
    )

    # print(movies_df["text"].head())
    # print(movies_df["text"].isna().sum())
    # print(movies_df["text"].str.len().describe())

    vectorizer = TfidfVectorizer(
        stop_words="english", 
        max_features=50000,
        min_df=2, # ignore words that appear in fewer than 2 movies
        max_df=0.85 # 
    )

    tfidf_matrix = vectorizer.fit_transform(movies_df["text"])

    nm_model = NearestNeighbors(
        metric="cosine",
        algorithm="brute",
        n_neighbors=50
    )

    nm_model.fit(tfidf_matrix)

    # movie_indices = {
    #     row["movie_id"]: index
    #     for index, row in movies_df.iterrows()
    # }

    with open(NM_MODEL_PATH, "wb") as f:
        pickle.dump(nm_model, f)

    with open(TFIDF_PATH, "wb") as f:
        pickle.dump(tfidf_matrix, f)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    with open(MOVIES_DF_PATH, "wb") as f:
        pickle.dump(movies_df, f)

    print(f"Built TF-IDF + nearest neighbor model for {len(movies_df)} movies.")


if __name__ == "__main__":
    build_movie_metadata_model()