import React from 'react';
import './../styles/landing.css';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import { useGenre } from '../GenreContext';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {

    // PRIMARILY A SEARCH BAR PAGE WITH NAVIGATION TO GENRES
    const {selectedGenre } = useGenre();
    const navigateTo = useNavigate();

    const handleSubmit = (event) => {
        event.preventDefault();
        const query = event.target.search.value;
        console.log('Search query:', query);
        // Here you can add logic to handle the search query, e.g., redirecting to a search results page
    }

    React.useEffect(() => {
        // If a genre is selected, navigate to the corresponding genre page
        if (selectedGenre) {
            navigateTo(`/genres/${selectedGenre}`);
        }
    }, [selectedGenre, navigateTo]);

    return (
        <div className='layout'>
            <Navbar />
            <main className='landing-main'>
                <h1> Movie Recommender </h1>

                <div className="intro-text">
                    <p> Love a movie? Find your next favorite. </p>
                    <p> Explore our collection of classics and modern films from the 20th and 21st centuries, tailored to your taste.
                    </p>
                </div>
               

                <form onSubmit={handleSubmit}>
                    <input type="text" id="search" placeholder="Search..." />
                    <button type="submit">Search</button>
                </form>

            </main>

            <Footer />
        
        </div>
    );
};

export default LandingPage;