from backend.app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    last_retained_rating_count = db.Column(db.Integer, default=0, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    db.relationship("Watchlist", backref="user", lazy=True)


class Watchlist(db.Model):
    __tablename__ = "watchlist"

    # many to many relationship between movies and users table.
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True)
    added_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))




