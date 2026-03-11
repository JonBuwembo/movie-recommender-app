import react from 'react';
import './MovieCard.css';

const MovieCard = ({ movie }: { movie: any }) => {
    return (
        <div className="movie-card">
            <img src={movie.poster_url} alt={`${movie.title} Poster`} className="movie-poster" />
            <div className="movie-info">
                <h2 className="movie-title">{movie.title}</h2>
                <p className="movie-year">{movie.release_year}</p> 
                <p className="movie-genre">{movie.genre}</p>
            </div>
        </div>
    );
}

export default MovieCard;