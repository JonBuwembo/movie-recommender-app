import react from 'react';
import { useEffect } from 'react';
import './MovieCard.css';
import { useNavigate } from 'react-router-dom';
import  MovieDetails from '../../pages/MovieDetails';
import { Trash2, Bookmark } from "lucide-react";

type watchListMovie = {
    movie_id: number;
};

const MovieCard = ({ movie, mode = "normal", onRemove}: { movie: any; mode?: string; onRemove?: (movieId: number) => void}) => {
    const navigateTo = useNavigate();
    const userId = JSON.parse(localStorage.getItem('user') || "null");
    const [watchlist, setWatchlist] = react.useState<watchListMovie[]>([]);

    const saved = watchlist.some(item => item.movie_id === movie.movie_id);


    useEffect(() => {
        fetch(`http://localhost:5000/api/watchlist/${userId}`, { method: "GET"})
            .then(res => res.json())
            .then(data => setWatchlist(data))
            .catch(err => console.error(err));
    }, []);

    

    const showDetails = (movie: any) => {
        navigateTo(`/movies/details/${movie.movie_id}`);
    }

    const addToWatchlist = async (
        e: react.MouseEvent<HTMLButtonElement>
    ) => {
        e.stopPropagation();

        try {
            const response = await fetch(`http://localhost:5000/api/watchlist/${userId}`, { 
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: userId,
                    movie_id: movie.movie_id
                })
            }
        )

        if (!response.ok) {
            console.log("Failed to add movie to watchlist!")
            return;
        }

        const data = await response.json();
        console.log(data);

        setWatchlist(prev => [...prev, {movie_id: movie.movie_id}]);


        } catch (error) {
            console.error("Failed to add to watchlist", error);
        }
        
    }

    const removeFromWatchlist = async (e: react.MouseEvent<HTMLButtonElement>) => {
        e.stopPropagation();

        if (!userId || userId === "undefined") {
            console.error("No valid user id found")
            return;
        }

        try {
            const response = await fetch(
                `http://localhost:5000/api/watchlist/${userId}/${movie.movie_id}`, {
                    method: "DELETE"
                }
            )

            if (!response.ok) {
                console.log("Failed to remove movie!");
                return;
            }

            onRemove?.(movie.movie_id);

            setWatchlist(prev => prev.filter(item => item.movie_id !== movie.movie_id));

        } catch (err) {
            console.error("Failed to remove from watchlist", err)
        }
    }

    return (
        <div className="movie-card" onClick={() => showDetails(movie)}>
            <img src={movie.poster_url} alt={`${movie.title} Poster`} className="movie-poster" />
            {/* element where you click a ribbon and it becomes fully colored from having no fill, indicating its added to the watchlist. 
            Therefore, we call the function addToWatchList() */}

            {mode === "watchlist" ? (
                <button
                    className="trash-btn"
                    onClick={removeFromWatchlist}
                >
                    <Trash2 className="trash-icon" size={20} />
                </button>
            ):(
                 <button
                    className={`bookmark-btn ${saved? 'saved': ''}`}
                    onClick={addToWatchlist}
                >
            
                    <Bookmark size={20} />
                </button>
            )}
         
        </div>
    );
}

export default MovieCard;