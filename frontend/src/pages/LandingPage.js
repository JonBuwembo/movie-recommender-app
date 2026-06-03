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
    const handleSearchSubmit = (event) => {
        event.preventDefault();

        // logic for searching from landing page.
        navigateTo(`/movies/search/${searchQuery}`);
        setSearchQuery(searchQuery);
        setSearchQuery(''); // Clear the search input after submission
    }


    React.useEffect(() => {

        const getRecommendations = async () => {

            try {
                const response = await authFetch("http://localhost:5000/api/recommendations");
                const data = await response.json();

                if(!response.ok) {
                    console.log("Failed to fetch homepage recommendations.");
                    return;
                }

                setRecommendations(data.recommendations.recommendations);

            } catch (err) {
                console.error("Error with recommendations:", err);
            }
           

        }

        getRecommendations();
        
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

            </main>
            <Footer />
        
        </div>
    );
};

export default LandingPage;