import react from 'react';
import './MovieCard.css';
import { useNavigate } from 'react-router-dom';
import  MovieDetails from '../../pages/MovieDetails';

const MovieCard = ({ movie }: { movie: any }) => {
    const navigateTo = useNavigate();

    const showDetails = (movie: any) => {
        navigateTo(`/movies/details/${movie.movie_id}`);
    }

    return (
        <div className="movie-card" onClick={() => showDetails(movie)}>
            <img src={movie.poster_url} alt={`${movie.title} Poster`} className="movie-poster" />
            <div className="movie-info">
                <h2 className="movie-title">{movie.title}</h2>
                <p className="movie-year">{movie.release_year}</p> 
            </div>
        </div>
    );
}

export default MovieCard;