from huggingface_hub import hf_hub_download
from .svd_recommender import SVDRecommender

model = None
hugging_repo="JonBuwembo/movie-recommender-models"


def load_svd_artifacts():
    global model

    model_path = hf_hub_download(
        repo_id=hugging_repo,
        filename="svd.pkl"
    )

    model = SVDRecommender().load(model_path)
    return model

def reload_svd_model():
    """
    If there is a model already existed, force a reload of that model. 
    """
    global model
    model = None
    load_svd_artifacts()

def get_model():
    """ 
    We only load the model once, we only load that model on the first recommendation.
    If there is an existing model already, then reuse that same model.
    """

    global model
    if model is None:
        load_svd_artifacts()
    return model

def get_reverse_movie_map():
    return get_model().reverse_movie_map

def get_user_map():
    return get_model().user_map

def get_movie_map():
    return get_model().movie_map

def get_movie_embeddings():
    return get_model().movie_embeddings

if __name__ == "__main__":
    reload_svd_model()