import react, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/global.css';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import MovieCard from '../components/MovieCard/MovieCard';
import '../styles/movies.css';
import { useGenre } from '../GenreContext';
import { useSearch } from '../SearchContext';
import InfiniteScroll from 'react-infinite-scroll-component';
import { useWatchlist } from '../useWatchlist';


const MoviesDisplay = () => {
    const {genreParam, userId} = useParams(); //read url for other pages
    const {queryParam} = useParams();

    const [displayedMovies, setDisplayedMovies] = react.useState([]);
    const [hasMore, setHasMore] = react.useState(true);

    const { watchlist } = useWatchlist();

    const [page, setPage] = react.useState(1); // Improving performance of application

    const [searchResults, setSearchResults] = react.useState({
        top_results: [],
        similar_movies: []
    });

    useEffect(() => { console.log('Displayed movies updated: ', displayedMovies); }, [displayedMovies]);
    

    const {selectedGenre, setSelectedGenre} = useGenre();

    const [loading, setLoading] = react.useState(false);
    const {searchQuery, setSearchQuery} = useSearch();

    const fetchMoviesBySearch = (query) => {
        setSearchQuery('');

        if (!query) {
            return;
        }

        setLoading(true);
        console.log('Fetching movies for search query:', query);
        const fetchURL = `http://localhost:5000/api/search/${encodeURIComponent(query.trim())}`;

        fetch(fetchURL)
            .then(response => response.json())
            .then(data => {
                setSearchResults(data)
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching movies:', error);
                setLoading(false);
            });
    };


    const fetchMovies = react.useCallback((genre, page = 1) => {
        setLoading(true);
       

        const fetchURL = genre 
        ? `http://localhost:5000/api/movies/${genre}?page=${page}&limit=48` 
        : `http://localhost:5000/api/movies?page=${page}&limit=48`;

        fetch(fetchURL)
            .then(response => response.json())
            .then(data => {

                if (data.length < 48) setHasMore(false);

                setDisplayedMovies(prev => page === 1 ? data : [...prev, ...data]);

                // just added this.
                if (genre) setSelectedGenre(genre);

                setLoading(false);
            })
            .catch(error =>{
                console.error('Error fetching movies:', error);
                setDisplayedMovies([]);
                setSelectedGenre(genre);
                setLoading(false);
            });

    }, [setSelectedGenre]);


    const fetchWatchlist = (userId) => {
        setSelectedGenre("watchlist");
        setLoading(true);
        const fetchURL = `http://localhost:5000/api/watchlist/${userId}`

        

        fetch(fetchURL)
            .then(response => response.json())
            .then(data => {
                setDisplayedMovies(data);
                setLoading(false);
            })
            .catch(error =>  {
                console.error("Error fetching watchlist:", error);
                setDisplayedMovies([]);
                setLoading(false);
            })
    }

    // Initial page load only
    useEffect(() => {
        setDisplayedMovies([]);
        setPage(1);
        setHasMore(true);
        setSearchResults({ top_results: [], similar_movies: [] })

        if (userId) {
            fetchWatchlist(userId);
        } else {
            fetchMovies(genreParam, 1);
        }

    }, [genreParam, userId, fetchMovies]);


    useEffect(() => {
        if (queryParam) return;
        window.scrollTo({ top: 0, behavior: 'instant' });
    }, [genreParam, userId]);

    // pagination only. Skips page 1 because 1 was initially loaded
    useEffect(() => {
        if (!hasMore) return;
        if (page === 1) return;
        if (userId) return; // no paginating on watchlist!

        fetchMovies(genreParam, page);
    }, [page, genreParam, fetchMovies])

    useEffect(() => {
        if (queryParam) {
            console.log('Fetching a particular movie:', queryParam);
            fetchMoviesBySearch(queryParam);
        }
    }, [queryParam]);

    // // For dynamic/live update of watchlist upon deletions.
    // useEffect(() => {
    //     if (selectedGenre === "watchlist") {
    //         // "movie" refers to movie in displayedMovies list
    //         // "item" is the alias name for a movie in the watchlist list
    //         // compare ids between these two lists, leave only ones that match

            
    //         setDisplayedMovies(list => list.filter(movie => watchlist.some(item => item.movie_id === movie.movie_id )))
    //     }
    // }, [watchlist])

    useEffect(() => {
        console.log("watchlist contents:", watchlist);
        console.log("displayedMovies contents:", displayedMovies);
    }, [watchlist, displayedMovies]);

    function renderMovies() {

        
        const moviesToDisplay = selectedGenre === "watchlist"
            ? displayedMovies.filter(movie => watchlist.some(item => Number(item.movie_id) === Number(movie.movie_id)))
            : displayedMovies;

        console.log("moviesToDisplay value: ", moviesToDisplay);

        console.log("render movies called")
        if (loading && displayedMovies.length === 0) {
            return <p>Loading movies... </p> 
        }
        
        if (searchResults.top_results.length > 0 && queryParam) {
            return (
                <>
                    <h3 className="center"> Top Results </h3>
                    <div className='movies-display'>
                        {searchResults.top_results.map(
                            movie => (
                            <MovieCard 
                                key={movie.movie_id} 
                                movie={movie} />
                        ))}
                    </div>
                    <h3 className='center'> Similar Movies </h3>
                    <div className='movies-display'>
                        {searchResults.similar_movies.map(
                            movie => (<MovieCard key={movie.movie_id} movie={movie} />
                        ))}
                    </div>
                </>
            ); 
        } else if (searchResults.top_results.length === 0 && queryParam) {
            return <h3>Whoops!! No results found for "{queryParam}".</h3>;
        } else if (moviesToDisplay.length > 0) {
            return (
                <InfiniteScroll
                    dataLength={moviesToDisplay.length}
                    next={() => setPage(prev => prev + 1)}
                    hasMore={hasMore}
                    endMessage={<p>No more movies.</p>}
                >
                    <div className='movies-display'>
                        {moviesToDisplay.map(movie => (
                            <MovieCard
                                key={movie.movie_id}
                                movie={movie}
                                mode={selectedGenre === "watchlist" ? "watchlist" : "normal"}
                            />
                        ))}
                    </div>
                </InfiniteScroll>
            );

        } else if (selectedGenre === "watchlist" && moviesToDisplay.length === 0) {
            return <h3> No movies found in Your Watchlist</h3>
        } else if (selectedGenre && moviesToDisplay.length === 0) {
            return <h3>No movies found for {selectedGenre}.</h3>
        } 

        return <p>No movies available.</p>
    }

    return(
        <div className='layout'>
            <Navbar />
            
            <main>
                {queryParam && <h2 />}

                {!queryParam && selectedGenre && selectedGenre !== "watchlist" && (
                    <h2 className='center'>Movies in {selectedGenre} genre</h2>
                )}

                {!queryParam && !selectedGenre && (
                    <h2 className='center'>Browse your favorite vintage movies here!</h2>
                )}

                {!queryParam && selectedGenre === "watchlist" && (
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