import { useAuth } from "./AuthContext";
import { useWatchlistContext } from "./WatchlistContext";


export const useWatchlist = () => {

    const {authFetch} = useAuth();

    const {watchlist, setWatchlist} = useWatchlistContext();

    const addToWatchlist = async (movieId: number) => {
            try {
                const response = await authFetch(`http://localhost:5000/api/watchlist/${movieId}`, { 
                    method: "POST"
                }).catch(error =>
                    {
                        if (error.message === "Unauthorized") {
                            return;
                        }

                        console.log(error)
                    }
                )

                if (!response) return;

                if (!response.ok) {
                    console.log("Failed to add movie to watchlist!")
                    return;
                }

                const data = await response.json();
                console.log(data);

                setWatchlist(prev => [...prev, {movie_id: movieId}]);

            } catch (error) {
                if (error instanceof Error && error.message === "Unauthorized") {
                   return;
                }
                console.error(error)
            }

        }
    
        const removeFromWatchlist = async (movieId: number) => {
    
            try {
                const response = await authFetch(
                    `http://localhost:5000/api/watchlist/${movieId}`, {
                        method: "DELETE"
                    }
                ).catch(error =>
                    {
                        if (error.message === "Unauthorized") {
                            return;
                        }

                        console.log(error)
                    }
                )

                if (!response) return;
    
                if (!response.ok) {
                    console.log("Failed to remove movie!");
                    return;
                }
    
                setWatchlist(prev => prev.filter(item => item.movie_id !== movieId));

            } catch (error) {
                if (error instanceof Error && error.message === "Unauthorized") {
                    return;
                }

                console.error(error);
            }
        }

    return {
        watchlist,
        setWatchlist,
        addToWatchlist,
        removeFromWatchlist
    }
}