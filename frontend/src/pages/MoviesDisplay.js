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
    const {genreParam} = useParams(); //read url for other pages
    const {queryParam} = useParams();



    const [displayedMovies, setDisplayedMovies] = react.useState([]);

    const [searchResults, setSearchResults] = react.useState({
        top_results: [],
        similar_movies: []
    });

    console.log('Displayed movies: ', displayedMovies);

    //const [selectedGenre, setSelectedGenre] = react.useState(null);
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
                console.log("Data recieved: ", data);
                //setDisplayedMovies(data);
                setSearchResults(data)
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching movies:', error);
                //setDisplayedMovies([]);
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

    useEffect(() => {
        if (queryParam) return;

        if (genreParam) {
            console.log('Fetching movies for genre:', genreParam);
            fetchMovies(genreParam);
        } else {
            fetchMovies(null);
        }
    }, [genreParam, queryParam]);

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
                    <h3> Top Results </h3>
                    <div className='movies-display'>
                        {searchResults.top_results.map(
                            movie => (<MovieCard key={movie.movie_id} movie={movie} />
                        ))}
                    </div>
                    <h3> Similar Movies </h3>
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
                {displayedMovies.map(movie => <MovieCard key={movie.movie_id} movie={movie} />)}
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

                {!queryParam && selectedGenre && (
                    <h2>Movies in {selectedGenre} genre</h2>
                )}

                {!queryParam && !selectedGenre && (
                    <h2>Browse your favorite vintage movies here!</h2>
                )}
                
                {/* Show all movie thumbnails in a genre here otherwise all movies */}

                {renderMovies()}
                
            </main>
            
            <Footer />
        </div>
    );
}

export default MoviesDisplay;