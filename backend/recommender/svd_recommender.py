
import joblib
import os
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
        self.movie_map = None
        self.user_map = None
        self.reverse_movie_map = None

    def train(self, matrix, movie_map=None, user_map=None):
        self.model.fit(matrix)

        self.movie_embeddings = self.model.components_.T

        self.movie_map = movie_map
        self.user_map = user_map

        if movie_map:
            self.reverse_movie_map = {
                col_id: movie_id
                for movie_id, col_id, in movie_map.items()
            }
        
        return self
        

    def save(self, path):
        # tmp_path = str(path) + ".tmp"
        joblib.dump(self, path)
        # os.replace(tmp_path, path)
    
    def load(self, path):
        return joblib.load(path)
    

    # HELPER ---------------------------------
    def get_movie_vector(self, movie_id):
        if self.movie_map is None:
            raise ValueError("Movie map is not found")
        
        if movie_id not in self.movie_map:
            return None

        index = self.movie_map[movie_id]
        return self.movie_embeddings[index]


