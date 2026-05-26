import {
    createContext,
    useContext,
    useEffect,
    useState
} from "react";

type WatchlistMovie = {
    movie_id: number
}

type WatchlistContextType = {
    watchlist: WatchlistMovie[];
    setWatchlist: React.Dispatch<
    React.SetStateAction<WatchlistMovie[]>
    >;
}

const WatchlistContext = createContext<WatchlistContextType | null> (
    null
);

export const WatchlistProvider = ({children}: { children: React.ReactNode}) => {
    const [watchlist, setWatchlist] = useState<WatchlistMovie[]>([]);
    const userId = JSON.parse(localStorage.getItem('user') || "null");

    // load watchlist with the watchlist data in the database! Crucial.
    useEffect(() => {
        if (!userId) return;
        fetch(`http://localhost:5000/api/watchlist/${userId}`)
            .then(response => response.json())
            .then(data => setWatchlist(data.map((movie : WatchlistMovie) => ({ movie_id: movie.movie_id }))))
            .catch(err => console.error(err));
    }, [userId]);

    return (
        <WatchlistContext.Provider
            value={{watchlist, setWatchlist}}
        >
            {children}
        </WatchlistContext.Provider>
    );
    
};

export const useWatchlistContext = () => {
    const context = useContext(WatchlistContext)

    if (!context) {
        throw Error("custom err: No watchlist provider")
    };
    
    return context;
}
