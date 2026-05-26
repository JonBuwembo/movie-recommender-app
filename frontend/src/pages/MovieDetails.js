import react from 'react';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import MovieCard from '../components/MovieCard/MovieCard';
import { useParams } from 'react-router-dom';
import '../styles/movieDetails.css';
import StarRating from '../components/StarRating/StarRating';
import { Bookmark} from "lucide-react";
import { useWatchlist } from '../useWatchlist';

const MovieDetails = () => {

    const {movieIdParam} = useParams();

    const {addToWatchlist, removeFromWatchlist, watchlist} = useWatchlist();

    const [moviePoster, setMoviePoster] = react.useState('');
    const [movieSummary, setMovieSummary] = react.useState('');
    const [movieGenres, setMovieGenres] = react.useState([]);
    const [movieReleaseYear, setMovieReleaseYear] = react.useState('');
    const [movieRating, setMovieRating] = react.useState('');
    const [movieTitle, setMovieTitle] = react.useState('');

    const [recommendations, setRecommendations] = react.useState([]);

    const [loading, setLoading] = react.useState(false);

    const userId = JSON.parse(localStorage.getItem("user") || null);

    const fetchMovie = (movieId) => { 
        setLoading(true);
    
        // Fetch movie details using the movieId from the URL
        // fetch(`http://localhost:5000/api/movies/${movieId}`)
        // Then set the movie details in state to display on the page
        const BASE_URL = process.env.NODE_ENV === 'production'? 
            `http://movie-recommender-backend.onrender.com`: `http://localhost:5000`;

        fetch(`${BASE_URL}/api/details/${encodeURIComponent(movieId)}`)
            .then(response => response.json())
            .then(data => {
                setMoviePoster(data.movie.poster_url);
                setMovieGenres(data.movie.genres);
                setMovieSummary(data.movie.overview);
                setMovieReleaseYear(data.movie.release_year);
                setMovieRating(data.movie.rating_avg);
                setMovieTitle(data.movie.title);
                setRecommendations(data.recommendations);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching movie details:', error);
                setLoading(false);
            })
    }
    

    react.useEffect(() => {
        if (!movieIdParam) return;
        fetchMovie(movieIdParam)
    }, [movieIdParam])

    if (loading) {
        return <p className="loading"> loading movies ...</p>
    }

    return (
        <div className='layout'>
            <Navbar />
 
            {/* When a user clicks on a movie, the details of that movie, summary, cast, and other relevant information are displayed here */}
            <main className="main-wrapper">
                <div className="grid-wrapper">

                    <aside className='movie-poster'>
                        {/* Movie Poster */}
                        <img src={moviePoster} alt="Movie Poster" />
                    </aside>

                    <section className='movie-details-info'>
                        <h2> {movieTitle} <span> ({movieReleaseYear})</span> </h2>

                        <div className="community-rating-pill">
                            ⭐ {4.2}
                            <span>(53 votes)</span>
                        </div>

                        {/* Movie Summary */}
                        <label> Summary </label>
                        <p>{movieSummary}</p>

                        {/* Movie Genres */}
                        <label> Genres </label>
                        <p>{movieGenres}</p>

                        {/* Movie Rating */}
                        {/* <label className="rating-label"> Average Rating </label>
                        <p>{Number(movieRating).toFixed(2)}</p> */}

                        {/* Rating of the movie */}
                        <div className="rating-section">
                            <span className="rating-label">Rate this movie</span>

                            <div className="rating-box">
                                <StarRating 
                                    movieId={movieIdParam}
                                 />
                            </div>

                            <button className='watchlist-btn' onClick={() => addToWatchlist(userId, movieIdParam)}> <Bookmark size={20}/> Add to Watchlist </button>
                        </div>

                    </section>
                </div>

                <section className='recommendations'>
                    {/* Movie Recommendations */}
                    <p> Similar Suggestions </p>
                    
                    <div className='movies-display'>
                        {recommendations.map(rec => (
                            <MovieCard key={rec.movie_id} movie={rec} />
                        ))}
                    </div>
                    
                </section>
            </main> 
            <Footer />
        </div>
    );
};

export default MovieDetails;