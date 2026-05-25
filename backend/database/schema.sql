-- tables created for movie recommendation application
-- particular database script can be run in dbeaver.
-- does not need to be in script folder

-- movies table improved.
DROP TABLE IF EXISTS Movies;
CREATE TABLE Movies (
    movie_id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    overview TEXT,
    poster_url VARCHAR(255),
    release_year INT,
    rating_avg FLOAT
);

-- genres table
drop table if exists genres;
CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)

-- connects both tables. no need for foreign keys in the above tables.
drop table if exists moviesgenres;
CREATE TABLE MoviesGenres (
    movie_id INT REFERENCES Movies(movie_id),
    genre_id INT REFERENCES Genres(genre_id),
    PRIMARY KEY (movie_id, genre_id)
)

create table  users (
	user_id INT primary key,
	username TEXT not NULL,
	password_hash TEXT not NULL
)

create table ratings (
	user_id INT,
	movie_id INT,
	primary key (user_id, movie_id), -- combination is unique, users can't rate the same movie twice.
	rating INT check (rating >= 1 and rating <= 5),
	rated_at timestamp,
	constraint fk_user_id foreign key (user_id) references users (user_id),
	constraint fk_movie_id foreign key (movie_id) references movies (movie_id)
)

create table watchlist (
	user_id INT,
	movie_id INT,
	primary key (user_id, movie_id), -- combination is unique, users can't add the same movie twice.
	added_at TIMESTAMP,
	constraint fk_user_id foreign key (user_id) references users (user_id),
	constraint fk_movie_id foreign key (movie_id) references movies (movie_id)
)


alter table movies 
ADD COLUMN movie_cast TEXT,
ADD COLUMN writers TEXT,
ADD COLUMN vote_avg FLOAT,
ADD COLUMN adult BOOLEAN;
