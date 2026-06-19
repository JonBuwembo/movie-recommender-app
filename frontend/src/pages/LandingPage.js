import React from 'react';
import './../styles/landing.css';
import './../styles/movies.css';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import { useGenre } from '../GenreContext';
import { useNavigate } from 'react-router-dom';
import { useSearch } from '../SearchContext';
import { useAuth } from '../AuthContext';
import MovieCard from '../components/MovieCard/MovieCard';


const LandingPage = () => {

    // PRIMARILY A SEARCH BAR PAGE WITH NAVIGATION TO GENRES
    const {selectedGenre } = useGenre();
    let {searchQuery, setSearchQuery} = useSearch();
    const navigateTo = useNavigate();

    const {authFetch} = useAuth();

    const [recommendations, setRecommendations] = React.useState([]);
    const [becauseURecs, setBecauseURecs] = React.useState([]); 
    const [movieTitle , setMovieTitle] = React.useState("");


    const handleSearchSubmit = (event) => {
        event.preventDefault();

        // logic for searching from landing page.
        navigateTo(`/movies/search/${searchQuery}`);
        setSearchQuery(searchQuery);
        setSearchQuery(''); // Clear the search input after submission
    }


    React.useEffect(() => {

        const getRecommendations = async () => {
            console.time("recommendations");

            try {
             
                const response = await authFetch("http://localhost:5000/api/recommendations")
                .catch(error => {
                    if (error.message === "Unauthorized") {
                        return;
                    }

                    console.error(error);
                });

                console.timeEnd("authFetch");
                const data = await response.json();

                if(!response.ok) {
                    console.log("Failed to fetch homepage collaberative recommendations.");
                    return;
                }

                setRecommendations(data.recommendations.recommendations);
                console.timeEnd("recommendations");

            } catch (err) {
                console.error("Error with recommendations:", err);
            }
        }

        const getBecauseUWatchedRecommendations = async () => {
            // console.time("because-you-watched");

            try {
                const response = await authFetch("http://localhost:5000/api/because-you-watched")
                .catch(error => {
                    if (error.message === "Unauthorized") {
                        return;
                    }

                    console.error(error);
                });
                const data = await response.json()

                if (!response.ok) {
                    console.log("Failed to fetch homepage collaberative recommendations.");
                    return;
                }
                
                setMovieTitle(data.movie_title);
                setBecauseURecs(data.recs);

                // console.timeEnd("because-you-watched");

            } catch (error) {
                console.log("Failed to fetch movie similarity recommendations for homepage")
            }
        }

        
        getRecommendations();
        getBecauseUWatchedRecommendations();
        
    },[navigateTo])

    return (
        <div className='layout'>
            <Navbar />
            <main className='landing-main'>

                <div className="hero-section">
                    <h1 className='hero-title'> Movie Recommender </h1>
                    <p className='hero-text'> Rate movies, build your watchlist, and get personalized recommendations. </p>
                </div>
               
                <form onSubmit={handleSearchSubmit}>
                    <input className='search-input' type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} id="search" placeholder="Search..." />
                </form>


                {/* Show recommended movies */}
                <h2 className='landing-subheader'>Recommended For You </h2>

                <div className='movie-row'>
                    {recommendations.map(movie => (
                        <MovieCard key={movie.movie_id} movie={movie} /> ))}
                </div>

                <h2 className='landing-subheader'>Because you watched {movieTitle} </h2>

                <div className='movie-row'>
                    {becauseURecs.map(movie => (
                        <MovieCard key={movie.movie_id} movie={movie} /> ))}
                </div>

            </main>
            <Footer />
        
        </div>
    );
};

export default LandingPage;