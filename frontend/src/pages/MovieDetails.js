import react from 'react';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import MovieCard from '../components/MovieCard/MovieCard';
import { useParams } from 'react-router-dom';
import '../styles/movieDetails.css';
import StarRating from '../components/StarRating/StarRating';
import { Bookmark, Film} from "lucide-react";
import { useWatchlist } from '../useWatchlist';
import { useAuth } from '../AuthContext';
import { useRef } from "react";
import config from '../config';


const MovieDetails = () => {

    const {movieIdParam} = useParams();

    const {authFetch} = useAuth();
    const {addToWatchlist, watchlist} = useWatchlist();

    const containerRef = useRef(null);

    // const [canScrollLeft, setCanScrollLeft] = react.useState(false);
    // const [canScrollRight, setCanScrollRight] = react.useState(true);


    const [moviePoster, setMoviePoster] = react.useState('');
    const [movieSummary, setMovieSummary] = react.useState('');
    const [movieGenres, setMovieGenres] = react.useState([]);
    const [movieReleaseYear, setMovieReleaseYear] = react.useState('');
    // const [movieRating, setMovieRating] = react.useState('');
    const [movieTitle, setMovieTitle] = react.useState('');


    const [recommendations, setRecommendations] = react.useState([]);

    const [watchStatus, setWatchedStatus] = react.useState(false);

    const [numVotes, setNumVotes] = react.useState(0);
    const [avgVote, setAvgVotes] = react.useState(0);
    
    const onWatchlist = watchlist.some(item => Number(item.movie_id) === Number(movieIdParam));
    

    react.useEffect(() => {
        const fetchWatchStatus = async () => {
            const response = await authFetch(`${config.API_URL}/api/watched`)
            .catch(error => {
                if (error.message === "Unauthorized") {
                    return
                }

                console.log(error)
            });

            if (!response) return;

            const data = await response.json();

            const watchedIds = data.map(movie => movie.movie_id);

            const isWatched = watchedIds.some(id => Number(id) === Number(movieIdParam));
            setWatchedStatus(isWatched);
        }
        
        fetchWatchStatus();

    },[movieIdParam])


    react.useEffect(() => {
        const fetchVoteMetrics = async () => {
            const response = await authFetch(`${config.API_URL}/api/votes/${movieIdParam}`)
            .catch(error => {
                if (error.message === "Unauthorized") {
                    return;
                }
            });

            const data = await response.json();

            if (!response) return;

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

        authFetch(`${config.API_URL}/api/details/${encodeURIComponent(movieId)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json()}
            )
            .then(data => {

                if (!data?.movie) {
                    console.error("Movie data missing:", data);
                    setLoading(false);
                    return;
                }

                setMoviePoster(data.movie.poster_url);
                setMovieGenres(data.movie.genres);
                setMovieSummary(data.movie.overview);
                setMovieReleaseYear(data.movie.release_year);
                // setMovieRating(data.movie.rating_avg);
                setMovieTitle(data.movie.title);
                setRecommendations(data.recommendations);

                console.log(recommendations)
                setLoading(false);
            })
            .catch(error => {
                if (error.message === "Unauthorized") {
                    return;
                }

                console.error(error);
            });
    }

    const setWatched = async (movieId) => {

        try {
            const options = {
                method: 'POST',
                body: JSON.stringify({
                    "movieId" : movieId
                })
            }

            const response = await authFetch(`${config.API_URL}:5000/api/watched`, options)
            .catch(error => {
                if (error.message === "Unauthorized") {
                    return;
                }

                console.error(error);
            });

            if (!response.ok) {
                console.log("unsuccessful in setting movie to complete status")
                return
            }

            setWatchedStatus(true);

        } catch (error) {
            if (error instanceof Error && error.message === "Unauthorized") {
                return; 
            }

            console.error(error);
        }
    }

    const scroll = (direction) => {
        const container = containerRef.current; // access DOM node
        if (!container) return;
        
        const card = container.querySelector(".movie-card");
        if (!card) return;

        const style = window.getComputedStyle(container);
        const gap = parseInt(style.gap || 0);
        const scrollAmount = (card.offsetWidth + gap) * 3;

        container.scrollBy({
            left: direction === "left" ? -scrollAmount : scrollAmount,
            behavior: "smooth",
        });

    };
    

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
                        {moviePoster ? (
                            <img src={moviePoster} alt="Movie Poster" />
                            ) : (
                                <div className='no-poster-screen-details'>
                                    <Film size={75} />
                                    <h2>{movieTitle}</h2>
                                </div>
                            )}

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
                        <p>{movieGenres === "Other" ? "No genres available" : movieGenres}</p>

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

                    <h3 className="similar-title"> Similar Suggestions </h3>

                    <div className='similar-wrapper'>

                        <button className="scroll-btn left" onClick={() => scroll("left")}>
                            ←
                        </button>

                        <div className='similar-container' ref={containerRef}>
                            
                            {recommendations.map(rec => (

                                <MovieCard key={rec.movie_id} movie={rec} page="recommend" />
                            ))}
                        </div>

                        <button className="scroll-btn right" onClick={() => scroll("right")}>
                             →
                        </button>

                    </div>
                </section>
            </main> 
            <Footer />
        </div>
    );
};

export default MovieDetails;