import { useWatchlistContext } from "./WatchlistContext";


export const useWatchlist = () => {

    const {watchlist, setWatchlist} = useWatchlistContext();

    const addToWatchlist = async (userId: string, movieId: number) => {
            try {
                const response = await fetch(`http://localhost:5000/api/watchlist/${userId}`, { 
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        movie_id: movieId
                    })
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
    
        const removeFromWatchlist = async (userId: string, movieId: number) => {
            if (!userId || userId === "undefined") {
                console.error("No valid user id found")
                return;
            }
    
            try {
                const response = await fetch(
                    `http://localhost:5000/api/watchlist/${userId}/${movieId}`, {
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