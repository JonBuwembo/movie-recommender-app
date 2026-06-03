

# Prevents API rewrites later

from .svd_recommender import (SVDRecommender)

def get_recommender():
    return SVDRecommender() # change to ALSRecommender when you migrate to it after testing and user numbers increase.

    