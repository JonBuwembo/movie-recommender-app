import React from 'react';
import './../styles/landing.css';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import { useGenre } from '../GenreContext';
import { useNavigate } from 'react-router-dom';
import { useSearch } from '../SearchContext';

const LandingPage = () => {

    // PRIMARILY A SEARCH BAR PAGE WITH NAVIGATION TO GENRES
    const {selectedGenre } = useGenre();
    let {searchQuery, setSearchQuery} = useSearch();
    const navigateTo = useNavigate();

    const handleSearchSubmit = (event) => {
        event.preventDefault();
        console.log('Search query:', searchQuery);
        // logic for searching from landing page.
        navigateTo(`/movies/${searchQuery}`);
        setSearchQuery(searchQuery);
        console.log('Search query set:', searchQuery);
        setSearchQuery(''); // Clear the search input after submission
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
               

                <form onSubmit={handleSearchSubmit}>
                    <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} id="search" placeholder="Search..." />
                    <button type="submit">Search</button>
                </form>

            </main>

            <Footer />
        
        </div>
    );
};

export default LandingPage;