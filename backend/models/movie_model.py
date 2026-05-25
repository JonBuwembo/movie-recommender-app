from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import Watchlist, User
import datetime


movie_genres = db.Table(
    "MovieGenres",
    db.Column("movie_id", db.Integer, db.ForeignKey("movies.movie_id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genres.genre_id"), primary_key=True)
)


class Movie(db.Model):

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, primary_key=True)
    overview = db.Column(db.Text(), nullable=False)
    poster_url = db.Column(db.String(1000))
    release_year = db.Column(db.Integer)
    rating_avg = db.Column(db.Float)
    movie_cast = db.Column(db.String(1000))
    writers = db.Column(db.String(1000))
    vote_avg = db.Column(db.Float) 
    adult = db.Column(db.Boolean)
    directors = db.Column(db.String(1000))

    # relationship
    ratings = db.relationship("Rating", backref="movie", lazy=True)
    watchlist = db.relationship("Watchlist", backref="movie", lazy=True)
    genres = db.relationship("Genre", secondary=movie_genres, back_populates="movies")

class Rating(db.Model):
    __tablename__ = "ratings"

    # user_id, movie_id, rating, rated_at
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id"), primary_key=True)
    rating = db.Column(db.Float, nullable=False)
    rated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Genre(db.Model):

    __tablename__ = "genres"

    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    movies = db.relationship("Movie", secondary=movie_genres, back_populates="genres")