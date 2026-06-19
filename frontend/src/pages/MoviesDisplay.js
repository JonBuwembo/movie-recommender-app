import react, { useEffect } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import '../styles/global.css';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import MovieCard from '../components/MovieCard/MovieCard';
import '../styles/movies.css';
import { useGenre } from '../GenreContext';
import { useSearch } from '../SearchContext';
import InfiniteScroll from 'react-infinite-scroll-component';
import { useWatchlist } from '../useWatchlist';
import { useAuth } from '../AuthContext';


const MoviesDisplay = () => {
    const {genreParam} = useParams(); //read url for other pages
    const {queryParam} = useParams();

    const location = useLocation();
    const isWatchlist = location.pathname.includes("/movies/watchlist");


    const {watchlist} = useWatchlist();
    const {authFetch, userId} = useAuth();

    const [displayedMovies, setDisplayedMovies] = react.useState([]);
    const [hasMore, setHasMore] = react.useState(true);
    const [hasFetched, setHasFetched] = react.useState(false);

    const [page, setPage] = react.useState(1); // Improving performance of application

    const [searchResults, setSearchResults] = react.useState({
        top_results: [],
        similar_movies: []
    });
    

    const {selectedGenre, setSelectedGenre} = useGenre();

    const [loading, setLoading] = react.useState(false);
    const {setSearchQuery} = useSearch();

    const fetchMoviesBySearch = (query) => {
        setSearchQuery('');

        if (!query) {
            return;
        }

        setLoading(true);
        const fetchURL = `http://localhost:5000/api/search/${encodeURIComponent(query.trim())}`;

        authFetch(fetchURL)
            .then(response => response.json())
            .then(data => {
                setSearchResults(data)
                setLoading(false);
                setHasFetched(true);
            })
            .catch(error => {
                if (error.message === "Unauthorized") {
                    return;
                }

                console.error(error);
                setLoading(false);
                setHasFetched(true);
            });
    };


    const fetchMovies = react.useCallback((genre, page = 1) => {
        setLoading(true);

        const fetchURL = genre 
        ? `http://localhost:5000/api/movies/${genre}?page=${page}&limit=48` 
        : `http://localhost:5000/api/movies?page=${page}&limit=48`;
     

        authFetch(fetchURL)
            .then(response => response.json())
            .then(data => {

                if (data.length < 48) setHasMore(false);

                setDisplayedMovies(prev => page === 1 ? data : [...prev, ...data]);

                // Important lines of code
                if (genre) setSelectedGenre(genre);
                if (!genre) setSelectedGenre("");

                setLoading(false);
            })
            .catch(error =>{
                if (error.message === "Unauthorized") {
                    return;
                }

                console.error(error);
                setDisplayedMovies([]);
                setSelectedGenre("");
                setLoading(false);
            });

    }, [setSelectedGenre]);


    const fetchWatchlist = react.useCallback(() => {
        setSelectedGenre(null);
        setLoading(true);
        const fetchURL = "http://localhost:5000/api/watchlist"


        authFetch(fetchURL)
            .then(response => response.json())
            .then(data => {
                setDisplayedMovies(data);
                setLoading(false);
            })
            .catch(error =>  {
                if (error.message === "Unauthorized") {
                    return;
                }

                console.error(error)
                setDisplayedMovies([]);
                setLoading(false);
            })
    }, [authFetch, setSelectedGenre])

    // Initial page load only
    useEffect(() => {
        setDisplayedMovies([]);
        setPage(1);
        setHasMore(true);
        setSearchResults({ top_results: [], similar_movies: [] })

        if (isWatchlist) {
            fetchWatchlist();
        } else {
            fetchMovies(genreParam, 1);
        }

    }, [genreParam, isWatchlist]);


    useEffect(() => {
        if (queryParam) return;
        window.scrollTo({ top: 0, behavior: 'instant' });
    }, [genreParam, userId]);

    // pagination only. Skips page 1 because 1 was initially loaded
    useEffect(() => {
        if (!hasMore) return;
        if (page === 1) return;
        if (isWatchlist) return; // no paginating on watchlist!

        fetchMovies(genreParam, page);
    }, [page, genreParam, fetchMovies])

    useEffect(() => {
        if (queryParam) {
            fetchMoviesBySearch(queryParam);
        }
    }, [queryParam]);


    function renderMovies() {

        
        const moviesToDisplay = isWatchlist
            ? displayedMovies.filter(movie => watchlist.some(item => Number(item.movie_id) === Number(movie.movie_id)))
            : displayedMovies;

        if (loading && displayedMovies.length === 0) {
            return <p>Loading movies... </p> 
        }

        // 2. Search mode
        if (queryParam) {
            if (!hasFetched) return <p>Loading movies...</p>

            if (searchResults.top_results.length === 0) {
                return <h3>Whoops!! No results found for "{queryParam}".</h3>
            }

            return (
                <>
                    <h3 className="center">Top Results</h3>
                    <div className="movies-display">
                        {searchResults.top_results.map(movie => (
                            <MovieCard key={movie.movie_id} movie={movie} />
                        ))}
                    </div>
                    <h3 className="center">Similar Movies</h3>
                    <div className="movies-display">
                        {searchResults.similar_movies.map(movie => (
                            <MovieCard key={movie.movie_id} movie={movie} />
                        ))}
                    </div>
                </>
            )
        }

        // 3. Normal / watchlist mode
        if (moviesToDisplay.length === 0) {
            return isWatchlist
                ? <h3>No movies found in your Watchlist.</h3>
                : selectedGenre
                    ? <h3>No movies found for {selectedGenre}.</h3>
                    : <p>No movies available.</p>
        }

        return (
            <InfiniteScroll
                dataLength={moviesToDisplay.length}
                next={() => setPage(prev => prev + 1)}
                hasMore={hasMore}
                endMessage={<p>No more movies.</p>}
            >
                <div className="movies-display">
                    {moviesToDisplay.map(movie => (
                        <MovieCard
                            key={movie.movie_id}
                            movie={movie}
                            mode={isWatchlist ? "watchlist" : "normal"}
                        />
                    ))}
                </div>
            </InfiniteScroll>
        )
    }

    return(
        <div className='layout'>
            <Navbar />
            
            <main className='movies-main'>
                {queryParam && <h2 />}

                {!queryParam && selectedGenre && !isWatchlist && (
                    <h2 className='center'>Movies in {selectedGenre} genre</h2>
                )}

                {!queryParam && !selectedGenre && !isWatchlist && (
                    <h2 className='center'>Browse your favorite vintage movies here!</h2>
                )}

                {!queryParam && isWatchlist && (
                    <h2 className='center'>Your Watchlist</h2>
                )}
                
                {/* Show all movie thumbnails in a genre here otherwise all movies */}

                {renderMovies()}
                
            </main>
            
            <Footer />
        </div>
    );
}

export default MoviesDisplay;