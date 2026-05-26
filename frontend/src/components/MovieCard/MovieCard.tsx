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

const MovieCard = ({ movie, mode = "normal"}: { movie: any; mode?: string} ) => {
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

   

    return (
        <div className="movie-card" onClick={() => showDetails(movie)}>
            <img src={movie.poster_url} alt={`${movie.title} Poster`} className="movie-poster" />
            {/* element where you click a ribbon and it becomes fully colored from having no fill, indicating its added to the watchlist. 
            Therefore, we call the function addToWatchList() */}

            {mode === "watchlist" ? (
                <button
                    className="trash-btn"
                    onClick={(e) => {e.stopPropagation(); removeFromWatchlist(userId, movie.movie_id)}}
                >
                    <Trash2 className="trash-icon" size={20} />
                </button>
            ):(
                 <button
                    className={`bookmark-btn ${saved? 'saved': ''}`}
                    onClick={(e) => {e.stopPropagation(); addToWatchlist(userId, movie.movie_id)}}
                >
            
                    <Bookmark size={20} />
                </button>
            )}
         
        </div>
    );
}

export default React.memo(MovieCard);