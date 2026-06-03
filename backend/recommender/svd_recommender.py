
import joblib
from sklearn.decomposition import (
    TruncatedSVD
)
# SVD Recommender meant for testing on a few users
# First recommender to build now. Later, migration to ALS
# migration will be simplified by inheriting the base.py recommender class.

class SVDRecommender:

    def __init__(self, n_components=50):
        self.model = (
            TruncatedSVD(
                n_components=n_components
            )
        )

        self.movie_embeddings = None

    def train(self, matrix):
        self.model.fit(matrix)
        self.movie_embeddings = self.model.components_.T
        

    def save(self, path):
        joblib.dump(
            {
                "model" : self.model,
                "movie_embeddings" : self.movie_embeddings
            },
            path
        )
    
    def load(self, path):
        data = joblib.load(path)
        self.model = data["model"]

        self.movie_embeddings = (
            data[
                "movie_embeddings"
            ]
        )

