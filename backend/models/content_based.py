import pickle
import os
from database.db_connection import get_db_connection
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SIMILARITY_MATRIX_PATH = os.path.join(BASE_DIR, 'artifacts', 'similarity_matrix.pkl')
TDFIDF_PATH = os.path.join(BASE_DIR, 'artifacts', 'tfidf_matrix.pkl')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'artifacts', 'tfidf_vectorizer.pkl')


# building movie index mapping dynamizally from the database
connection = get_db_connection()
cursor = connection.cursor()
query = """
SELECT 
    m.movie_id, 
    m.title, 
    m.overview, 
    m.release_year, 
    m.rating_avg,
    m.poster_url, 
    STRING_AGG(g.name, ', ') AS genres
FROM movies m 
JOIN "MovieGenres" mg ON m.movie_id = mg.movie_id 
JOIN genres g ON mg.genre_id = g.genre_id
GROUP BY m.movie_id, m.title, m.overview, m.release_year, m.rating_avg, m.poster_url;
"""
cursor.execute(query)

movies_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

# another field for concatenated text used for building similarity matrix.
movies_df['text'] = movies_df['overview'].fillna('') + ' ' + movies_df['overview'].fillna('')  + ' ' + movies_df['genres'].fillna('') + ' ' + movies_df['title'].fillna('') 

corpus = movies_df['text'].tolist()

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(corpus)
similarity_matrix = cosine_similarity(tfidf_matrix)

with open(SIMILARITY_MATRIX_PATH, 'wb') as f:
    pickle.dump(similarity_matrix, f)

with open(TDFIDF_PATH, 'wb') as f:
    pickle.dump(tfidf_matrix, f)

with open(VECTORIZER_PATH, 'wb') as f:
    pickle.dump(vectorizer, f)

# movie_indices = {title: idx for idx, title in enumerate(movies_df['title'])}
movie_indices = pd.Series(movies_df.index, index=movies_df['title']).to_dict()

def get_similar_movies(movie_index, top_n=10, offset=0):
    scores = list(enumerate(similarity_matrix[movie_index]))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    similar_indices = [i for i, _ in scores[1 + offset : top_n + offset + 1]]
    # iloc: integer-location based indexing for selection by position
    return movies_df.iloc[similar_indices][['title', 'overview', 'release_year', 'rating_avg', 'poster_url']].to_dict(orient='records')