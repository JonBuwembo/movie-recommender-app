import React from 'react';
import { useRef } from 'react';
import { ChevronLeft, ChevronRight} from "lucide-react";

import './../styles/landing.css';
import './../styles/movies.css';

import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';

import { useGenre } from '../GenreContext';
import { useNavigate } from 'react-router-dom';

import { useSearch } from '../SearchContext';
import { useAuth } from '../AuthContext';
import MovieCard from '../components/MovieCard/MovieCard';

import config from '../config';


const LandingPage = () => {

    // PRIMARILY A SEARCH BAR PAGE WITH NAVIGATION TO GENRES
    let {searchQuery, setSearchQuery} = useSearch();
    const navigateTo = useNavigate();

    const [loading, setloading] = React.useState(false);
    const {authFetch} = useAuth();

    const [recommendations, setRecommendations] = React.useState([]);
    const [becauseURecs, setBecauseURecs] = React.useState([]); 
    const [movieTitle , setMovieTitle] = React.useState("");


    const recommendationRef = useRef(null);
    const becauseRef = useRef(null);

    const scroll = (ref, direction) => {
        if (ref.current) {
            ref.current.scrollBy({
                left: direction * ref.current.clientWidth,
                behavior: "smooth"
            });
        }
        
    }


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
                setloading(true);

                const response = await authFetch(`${config.API_URL}/api/recommendations`)
                .catch(error => {
                    if (error.message === "Unauthorized") {
                        return;
                    }

                    console.error(error);
                });

            
                const data = await response.json();

                if(!response.ok) {
                    console.log("Failed to fetch homepage collaberative recommendations.");
                    return;
                }

                setloading(false);
                setRecommendations(data.recommendations);
                console.log("recommendation: ", recommendations)
                
            

            } catch (err) {
                console.error("Error with recommendations:", err);
            }
        }

        const getBecauseUWatchedRecommendations = async () => {
            // console.time("because-you-watched");

            try {
                setloading(true);

                const response = await authFetch(`${config.API_URL}/api/because-you-watched`)
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
                
                setloading(false);
                setMovieTitle(data.movie_title);
                setBecauseURecs(data.recs);

                // console.timeEnd("because-you-watched");

            } catch (error) {
                console.log("Failed to fetch movie similarity recommendations for homepage")
            }
        }

        
        getRecommendations();
        getBecauseUWatchedRecommendations();
        
    },[navigateTo, authFetch])



    const renderRecommendations = () => {

        if (loading) {
            return (
                <div className='loading-page'>
                    <div className='loading-shimmer'></div>
                </div>
            );
        }

        return (
              <section className="carasoul-section">
                    {/* Show recommended movies */}
                    <div className='display-gap'>
                        <h2 className='landing-subheader'>Recommended For You </h2>

                        <div className="carousel-wrapper">
                            <button onClick={() => scroll(recommendationRef, -1)} className="carousel-arrow left"> <ChevronLeft size={30} /> </button>

                                <div className="movie-row-container" ref={recommendationRef}>
                                    <div className='movie-row'>
                                        {recommendations.map(movie => (
                                            <MovieCard key={movie.movie_id} movie={movie} /> ))}
                                    </div>
                                </div>
                            
                            <button onClick={() => scroll(recommendationRef, 1)}className='carousel-arrow right'> <ChevronRight size={30} /></button>
                        </div>
                    </div>

                    {becauseURecs.length > 0 && (
                        <>
                            <div className='display-gap'>
                                <h2 className='landing-subheader'>Because you watched {movieTitle} </h2>

                                <div className="carousel-wrapper">
                                    <button onClick={() => scroll(becauseRef, -1)} className="carousel-arrow left"> <ChevronLeft size={30} /> </button>

                                        <div className="movie-row-container" ref={becauseRef}>
                                            <div className='movie-row'>
                                                {becauseURecs.map(movie => (
                                                    <MovieCard key={movie.movie_id} movie={movie} /> ))}
                                            </div>
                                        </div>

                                    <button onClick={() => scroll(becauseRef, 1)} className='carousel-arrow right'> <ChevronRight size={30} /></button>
                                </div>
                            </div>
                        </>
                    )}
            
            </section>
        )
    }

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
            </main>


            {renderRecommendations()}
            
            <Footer />
        </div>
    );
};

export default LandingPage;