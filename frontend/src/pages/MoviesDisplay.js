import react, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/global.css';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import MovieCard from '../components/MovieCard/MovieCard';
import '../styles/movies.css';
import { useGenre } from '../GenreContext';
import { useSearch } from '../SearchContext';

const MoviesDisplay = () => {
    const {genreParam, userId} = useParams(); //read url for other pages
    const {queryParam} = useParams();



    const [displayedMovies, setDisplayedMovies] = react.useState([]);

    const [searchResults, setSearchResults] = react.useState({
        top_results: [],
        similar_movies: []
    });

    console.log('Displayed movies: ', displayedMovies);

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


    const fetchMovies = (genre) => {
        setLoading(true);
        console.log('Fetching movies for genre:', genre);
        const fetchURL = genre ? `http://localhost:5000/api/movies/${genre}` : 'http://localhost:5000/api/movies';

        fetch(fetchURL)
            .then(response => response.json())
            .then(data => {
                setDisplayedMovies(data);
                setSelectedGenre(genre);
                setLoading(false);
            })
            .catch(error =>{
                console.error('Error fetching movies:', error);
                setDisplayedMovies([]);
                setSelectedGenre(genre);
                setLoading(false);
            });
    };


    const fetchWatchlist = (userId) => {
        // 
        setLoading(true);
        const fetchURL = `http://localhost:5000/api/watchlist/${userId}`

        fetch(fetchURL)
            .then(response => response.json())
            .then(data => {
                setDisplayedMovies(data);
                setSelectedGenre("watchlist");
                setLoading(false);
            })
            .catch(error =>  {
                console.error("Error fetching watchlist:", error);
                setDisplayedMovies([]);
                setLoading(false);
            })
    }


    useEffect(() => {
        if (queryParam) return;

        if (userId) {
            fetchWatchlist(userId);
        } else if (genreParam) {
            console.log('Fetching movies for genre:', genreParam);
            fetchMovies(genreParam);
        } else {
            fetchMovies(null);
        }
    }, [genreParam, queryParam, userId]);

    useEffect(() => {
        if (queryParam) {
            console.log('Fetching a particular movie:', queryParam);
            fetchMoviesBySearch(queryParam);
        }
    }, [queryParam]);

    function renderMovies() {
        if (loading) {
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
        } else if (displayedMovies.length > 0 ) {
            return (
            <div className='movies-display'>
                {displayedMovies.map(movie => (
                    <MovieCard 
                        key={movie.movie_id} 
                        movie={movie}
                        mode={selectedGenre === "watchlist" ? "watchlist" : "normal"} 
                        onRemove={(movieId) => {
                            setDisplayedMovies(prev => prev.filter(movie => movie.movie_id !== movieId))
                        }}
                    />
                ))}
            </div>
            );

        } else if (selectedGenre && displayedMovies.length === 0) {
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