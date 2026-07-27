import pandas as pd
from backend.app import create_app, db
from backend.models.user import User
from backend.models.movie_model import Rating, Movie
from werkzeug.security import generate_password_hash
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent

ratings_df = pd.read_csv(BASE_DIR / "csvs" / "ratings.csv")
links_df = pd.read_csv(BASE_DIR / "csvs" / "links.csv")
movies_df = pd.read_csv(BASE_DIR / "csvs" / "movies.csv") # Need to map Movie lens movie id to your movie id

app = create_app()

def normalize_title(title):
    title = title.lower()

    # remove they year
    title = re.sub(r"\(\d{4}\)", "", title)

    # remove any punctuation
    title = re.sub(r"[^a-z0-9 ]", "", title)

    # remove extra spaces
    title = title.strip()

    return title


with app.app_context():
    movies = Movie.query.all()

    # a lookup, mapping title to movie_id
    db_title_map = {
        normalize_title(movie.title): movie.movie_id
        for movie in movies
    }

   
    # Passes movie lens titles into normalize_title()
    movies_df["normalized_title"] = (
        movies_df["title"]
        .apply(normalize_title)
    )

    # maps title to database id
    movies_df["db_movie_id"] = (
        movies_df["normalized_title"]
        .map(db_title_map)
    )

    # drop any movies app doesn't know (NaN)
    movies_df = movies_df.dropna(
        subset=["db_movie_id"]
    )

    # creates the mapping for movieId in movielens -> database movie id
    movielens_to_db = dict(
        zip(
            movies_df["movieId"],
            movies_df["db_movie_id"]
        )
    )

    next_user_id = 1000000

    movielens_users = ratings_df["userId"].unique()

    # MovieLens ID -> Database ID
    user_mapping = {}

    existing_usernames = {u.username for u in User.query.with_entities(User.username).all()}

    disabled_password_hash = generate_password_hash("disabled")

    for ml_user in movielens_users:
        new_user_id = next_user_id
        username=f"ml_user_{ml_user}"

        if username in existing_usernames:
            continue


        user = User(
            user_id=new_user_id,
            username=f"ml_user_{ml_user}",
            password_hash=disabled_password_hash,
        )
    
        db.session.add(user)
        user_mapping[ml_user] = new_user_id
        next_user_id += 1
    db.session.commit()

    rating_objects = []

    BATCH_SIZE = 2_000
    batch = []
    committed = 0
    seen_pairs = set() # set()

    for _, row in ratings_df.iterrows():

        ml_movie_id = row["movieId"] # in the form of "np.number"
        ml_user_id = row["userId"]
        their_rating = row["rating"]

        if ml_movie_id not in movielens_to_db:
            continue

        if ml_user_id not in user_mapping:
            continue

        database_movie_id = movielens_to_db[ml_movie_id]
        database_user_id = user_mapping[ml_user_id]

        pair = (database_movie_id, database_user_id)

        if pair in seen_pairs:
            continue

        seen_pairs.add(pair)

        batch.append(
            Rating(
                user_id=int(database_user_id),
                movie_id=int(database_movie_id),
                rating=float(their_rating)
            )
        )

        if len(batch) >= BATCH_SIZE:
            db.session.bulk_save_objects(batch)
            db.session.commit()
            committed += len(batch)
            print(f"Successfully committed {committed} synthetic users w/ratings")
            batch = []

    # leftovers in batch
    if batch:
        db.session.bulk_save_objects(batch)
        db.session.commit()
        committed += len(batch)
        print(f"Successfully committed {committed} synthetic users w/ratings")
    
    print("")
    print("Done ...")
    print(f"Imported ratings: {len(rating_objects)}")
    print(f"Created users: {len(user_mapping)}")
    print(f"Movies matched: {len(movielens_to_db)}")
