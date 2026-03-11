import react from 'react';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';


const ResultsPage = () => {

    return (
        <div>

            <Navbar />

            <h2>Results Page</h2>
            {/* Show search results of search query, and all recommended movies. */}
            {/* What pops up is the one movie matching the search query, if no movies exists, shows a message. */}

            <Footer />
        </div>
    );
}

export default ResultsPage;