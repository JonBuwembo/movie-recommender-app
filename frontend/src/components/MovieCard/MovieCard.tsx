import React from 'react';
import { useEffect } from 'react';
import './MovieCard.css';
import { useNavigate } from 'react-router-dom';
import  MovieDetails from '../../pages/MovieDetails';
import { Trash2, Bookmark } from "lucide-react";
import { useWatchlist } from '../../useWatchlist';

type watchListMovie = {
    movie_id: number;
};

const MovieCard = ({ movie, mode = "normal", page = ""}: { movie: any; mode?: string; page?: string} ) => {
    const navigateTo = useNavigate();
    const userId = JSON.parse(localStorage.getItem('user') || "null");
    // const [watchlist, setWatchlist] = react.useState<watchListMovie[]>([]);

    const { addToWatchlist, removeFromWatchlist, watchlist, setWatchlist } = useWatchlist();

    const saved = watchlist.some(item => item.movie_id === movie.movie_id);


    // useEffect(() => {
    //     fetch(`http://localhost:5000/api/watchlist/${userId}`, { method: "GET"})
    //         .then(res => res.json())
    //         .then(data => setWatchlist(data))
    //         .catch(err => console.error(err));
    // }, []);

    

    const showDetails = (movie: any) => {
        navigateTo(`/movies/details/${movie.movie_id}`);
    }

    if (!movie.poster_url) {
        return (
            <div className='movie-card'>
                <div className='no-poster-screen' onClick={() => showDetails(movie)}>
                    <h1>{movie.title}</h1>

                    {mode === "watchlist" ? (
                    <button
                            className="trash-btn"
                            onClick={(e) => {e.stopPropagation(); removeFromWatchlist(movie.movie_id)}}
                        >
                            <Trash2 className="trash-icon" size={20} />
                        </button>
                    ):(
                        <button
                            className={`bookmark-btn ${saved? 'saved': ''}`}
                            onClick={(e) => {e.stopPropagation(); addToWatchlist(movie.movie_id)}}
                        >
                    
                            <Bookmark size={20} />
                        </button>
                    )}
                </div>
            </div>
        )
    }

   

    return (
        <div className={`movie-card ${page}`} onClick={() => showDetails(movie)}>
            <img src={movie.poster_url} alt={`${movie.title} Poster`} className="movie-poster" />
            {/* element where you click a ribbon and it becomes fully colored from having no fill, indicating its added to the watchlist. 
            Therefore, we call the function addToWatchList() */}

            {mode === "watchlist" ? (
                <button
                    className="trash-btn"
                    onClick={(e) => {e.stopPropagation(); removeFromWatchlist(movie.movie_id)}}
                >
                    <Trash2 className="trash-icon" size={20} />
                </button>
            ):(
                <button
                    className={`bookmark-btn ${saved? 'saved': ''}`}
                    onClick={(e) => {e.stopPropagation(); addToWatchlist(movie.movie_id)}}
                >
            
                    <Bookmark size={20} />
                </button>
            )}
         
        </div>
    );
}

export default React.memo(MovieCard);