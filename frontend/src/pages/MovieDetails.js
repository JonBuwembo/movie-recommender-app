import react from 'react';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';

const MovieDetails = () => {
    return (
        <div className='layout'>
            <Navbar />
            <h1>Movie Details</h1>
            {/* When a user clicks on a movie, the details of that movie, summary, cast, and other relevant information are displayed here */}

            <Footer />
        </div>
    );
};

export default MovieDetails;