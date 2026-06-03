import react from 'react';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import MovieCard from '../components/MovieCard/MovieCard';
import { useParams } from 'react-router-dom';
import '../styles/movieDetails.css';
import StarRating from '../components/StarRating/StarRating';
import { Bookmark} from "lucide-react";
import { useWatchlist } from '../useWatchlist';
import { useAuth } from '../AuthContext';

const MovieDetails = () => {

    const {movieIdParam} = useParams();

    const {authFetch} = useAuth();
    const {addToWatchlist, removeFromWatchlist, watchlist} = useWatchlist();

    const [moviePoster, setMoviePoster] = react.useState('');
    const [movieSummary, setMovieSummary] = react.useState('');
    const [movieGenres, setMovieGenres] = react.useState([]);
    const [movieReleaseYear, setMovieReleaseYear] = react.useState('');
    const [movieRating, setMovieRating] = react.useState('');
    const [movieTitle, setMovieTitle] = react.useState('');


    const [recommendations, setRecommendations] = react.useState([]);

    const [watchStatus, setWatchedStatus] = react.useState(false);

    const [numVotes, setNumVotes] = react.useState(0);
    const [avgVote, setAvgVotes] = react.useState(0);
    
    const onWatchlist = watchlist.some(item => Number(item.movie_id) === Number(movieIdParam));
    

    react.useEffect(() => {
        const fetchWatchStatus = async () => {
            const response = await authFetch("http://localhost:5000/api/watched");
            const data = await response.json();
            console.log("watched data:", data);

            const watchedIds = data.map(movie => movie.movie_id);

            const isWatched = watchedIds.some(id => Number(id) == Number(movieIdParam));
            setWatchedStatus(isWatched);
        }
        
        fetchWatchStatus();

    },[movieIdParam])


    react.useEffect(() => {
        const fetchVoteMetrics = async () => {
            const response = await authFetch(`http://localhost:5000/api/votes/${movieIdParam}`)
            const data = await response.json();

            console.log(data)

            setNumVotes(data.vote_count.toFixed(1))
            setAvgVotes(Number(data.avg_rating).toFixed(2))
        }

        fetchVoteMetrics();
    },[movieIdParam])


    const [loading, setLoading] = react.useState(false);

    const fetchMovie = (movieId) => { 
        setLoading(true);
    
        // Fetch movie details using the movieId from the URL
        // fetch(`http://localhost:5000/api/movies/${movieId}`)
        // Then set the movie details in state to display on the page
        const BASE_URL = process.env.NODE_ENV === 'production'? 
            `http://movie-recommender-backend.onrender.com`: `http://localhost:5000`;

        authFetch(`${BASE_URL}/api/details/${encodeURIComponent(movieId)}`)
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

    const setWatched = async (movieId) => {

        try {
            const options = {
                method: 'POST',
                body: JSON.stringify({
                    "movieId" : movieId
                })
            }

            const response = await authFetch("http://localhost:5000/api/watched", options)

            if (!response.ok) {
                console.log("unsuccessful in setting movie to complete status")
                return
            }

            setWatchedStatus(true);

        } catch (error) {
            console.error('Error setting movie to complete:', error)
        }
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
                            ⭐ {avgVote}
                            <span>({numVotes} votes)</span>
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

                            <div className='movie-actions'>

                                <button className={`watchlist-btn ${onWatchlist? 'yes' : ''}`} onClick={() => addToWatchlist(movieIdParam)}> 
                                    <Bookmark size={20}/> Add to Watchlist 
                                </button>

                                <button className={`completed-btn ${watchStatus ? 'yes' : ''}`} onClick={() => setWatched(movieIdParam)}> 
                                    <Bookmark size={20}/> Completed 
                                </button>
                            </div>
                           
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