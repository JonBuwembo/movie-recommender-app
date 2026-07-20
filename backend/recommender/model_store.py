
from huggingface_hub import hf_hub_download
import joblib
from .svd_recommender import SVDRecommender

model = None
movie_embeddings = None
movie_map = None
user_map = None
reverse_movie_map = None

hugging_repo="JonBuwembo/movie-recommender-models"


def load_svd_artifacts():
    global model, movie_embeddings, movie_map, user_map, reverse_movie_map

    model_path = hf_hub_download(
        repo_id=hugging_repo,
        filename="svd.pkl"
    )

    model = SVDRecommender().load(model_path)

    movie_map = model.movie_map
    user_map = model.user_map
    movie_embeddings = model.movie_embeddings

    if movie_map:
        reverse_movie_map = {
            col_id : movie_id
            for movie_id, col_id
            in movie_map.items()
        }
    return reverse_movie_map

def reload_svd_model():
    global model
    model = None
    load_svd_artifacts()

def get_model():
    global model
    if model is None:
        load_svd_artifacts()
    return model

def set_model(new_model):
    global model
    model = new_model

if __name__ == "__main__":
    reload_svd_model()