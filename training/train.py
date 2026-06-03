import pandas as pd
import joblib

import requests
import sys

import os
import time
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent / ".env"

BASE_DIR = Path(__file__).resolve().parent
backend_path = BASE_DIR.parent / "backend"
models_path = backend_path / "models" / "rec_models"

load_dotenv(dotenv_path=dotenv_path)
sys.path.append(str(backend_path))


from database.db_connection import get_db_connection

from recommender.svd_recommender import SVDRecommender

from scipy.sparse import (
    csr_matrix
)

from sqlalchemy import (
    create_engine
)




connection = get_db_connection()
cursor = connection.cursor()

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
# print(ratings.shape)
# print(ratings.head())
# print("ratings shape:", ratings.shape)
# print("unique users:", ratings.user_id.nunique())
# print("unique movies:", ratings.movie_id.nunique())

# building a dictionary
# enumerate automatically increments row_id and col_id
user_map = {
    user : row_id
    for row_id, user in enumerate(
        ratings.user_id.unique()
    )
}

movie_map = {
    movie: col_id
    for col_id, movie in enumerate(
        ratings.movie_id.unique()
    )
}

ratings["rating"] = pd.to_numeric( ratings["rating"], errors="coerce")
ratings = ratings.dropna(subset=["rating"])

# matrices need indices, help identify location row/col in matrix
# build matrix: 
#       row -> each user (row_index, user_id)
#       col -> each movie  (col_index, movie_id)
rows = ratings.user_id.map(user_map)
cols = ratings.movie_id.map(movie_map)

# print("RAW movie_id unique:", ratings.movie_id.unique()[:10])
# print("movie_map size:", len(movie_map))
# print("sample movie_ids:", ratings.movie_id.head(10))

matrix = csr_matrix(
    (ratings.rating, (rows, cols))
)


model = (SVDRecommender())
model.train(matrix)
model.save(models_path / "svd.pkl")
joblib.dump(movie_map, models_path / "movie_map.pkl")
joblib.dump(user_map, models_path / "user_map.pkl")

connection.close()


