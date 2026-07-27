import pandas as pd
import joblib

import sys

import os
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent / ".env"
BASE_DIR = Path(__file__).resolve().parent
backend_path = BASE_DIR.parent
models_path = backend_path / "models" / "rec_models"
sys.path.append(str(backend_path))


from database.db_connection import get_db_connection
from recommender.svd_recommender import SVDRecommender
from huggingface_hub import login, upload_file
from recommender.model_store import reload_svd_model

from scipy.sparse import (
    csr_matrix
)

load_dotenv(dotenv_path=dotenv_path)

hugging_face_key = os.getenv("HUGGINGFACE_API_KEY")

if hugging_face_key is None:
    raise ValueError("Hugging Face Key in .env cannot be read or is not found!")

hugging_repo = "JonBuwembo/movie-recommender-models"
login(hugging_face_key)

from sqlalchemy import (
    create_engine
)

def retrain_svd_pipeline(): 
    """
    SVD model training pipeline
    SVD model based on user ratings
    """
    connection = get_db_connection()
    cursor = connection.cursor()


    try:
        query_ratings = """
        SELECT
            user_id,
            movie_id,
            rating
        FROM ratings
        """

        cursor.execute(query_ratings)
        rows = cursor.fetchall()

        ratings = pd.DataFrame(rows, columns=["user_id", "movie_id", "rating"])

        # filtering
        ratings["rating"] = pd.to_numeric( ratings["rating"], errors="coerce")
        ratings = ratings.dropna(subset=["rating"])

        print("Ratings:", len(ratings))
        print("Unique users:", ratings.user_id.nunique())
        print("Unique movies:", ratings.movie_id.nunique())

        # mapping
        user_map = {
            user : row_id
            for row_id, user in enumerate(
                ratings.user_id.unique()
            )
        }

        print("Users in user map:", len(user_map))

        movie_map = {
            movie: col_id
            for col_id, movie in enumerate(
                ratings.movie_id.unique()
            )
        }


        rows = ratings.user_id.map(user_map)
        cols = ratings.movie_id.map(movie_map)

        matrix = csr_matrix(
            (ratings.rating, (rows, cols))
        )

        model = (SVDRecommender())
        model.train(matrix, movie_map, user_map)
        model.save(models_path / "svd.pkl")

        return model
    finally:
        cursor.close()
        connection.close()

def upload():

    """
    Pushing updated SVD model file to Hugging Face
    """

    print("uploading to hugging face")

    upload_file(
        path_or_fileobj=models_path / "svd.pkl",
        path_in_repo="svd.pkl",
        repo_id=hugging_repo,
        repo_type="model"
    )

    print("Finished uploading")


def retrain_model():
    """
    Trigger Model retraining
    """

    model = retrain_svd_pipeline()
    model.save(models_path / "svd.pkl")
    reload_svd_model() # avoids caching old model

    upload()


if __name__ == "__main__":
    retrain_model()
