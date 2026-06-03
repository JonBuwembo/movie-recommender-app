import { useAuth } from "./AuthContext";
import { useWatchlistContext } from "./WatchlistContext";


export const useWatchlist = () => {

    const {authFetch} = useAuth();

    const {watchlist, setWatchlist} = useWatchlistContext();

    const addToWatchlist = async (movieId: number) => {
            try {
                const response = await authFetch(`http://localhost:5000/api/watchlist/${movieId}`, { 
                    method: "POST"
                })

                if (!response.ok) {
                    console.log("Failed to add movie to watchlist!")
                    return;
                }

                const data = await response.json();
                console.log(data);

                setWatchlist(prev => [...prev, {movie_id: movieId}]);

            } catch (err) {
                console.error("Failed to add from watchlist", err)
            }

        }
    
        const removeFromWatchlist = async (movieId: number) => {
    
            try {
                const response = await authFetch(
                    `http://localhost:5000/api/watchlist/${movieId}`, {
                        method: "DELETE"
                    }
                )
    
                if (!response.ok) {
                    console.log("Failed to remove movie!");
                    return;
                }
    
                setWatchlist(prev => prev.filter(item => item.movie_id !== movieId));

    
            } catch (err) {
                console.error("Failed to remove from watchlist", err)
            }
        }

    return {
        watchlist,
        setWatchlist,
        addToWatchlist,
        removeFromWatchlist
    }
}