import react, { useEffect } from 'react';
import '../styles/global.css';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import MovieCard from '../components/MovieCard/MovieCard';
import '../styles/movies.css';

const MoviesDisplay = () => {
    const [movies, setMovies] = react.useState([]);
    
    useEffect(() => {
        // Fetch movies from the backend API and set them in state 
        fetch('http://localhost:5000/api/movies', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                console.log('Movies data:', data);

                if (Array.isArray(data)) {
                    console.log('Movies data is an array:', data);
                    setMovies(data);
                } else {
                    console.error('Movies data is not an array:', data);
                }
            })
            .catch(error => console.error('Error fetching movies:', error));

    }, []);

    return (
        <div className='layout'>
            <Navbar />
            
            <main>
                <h2>Movies Display Page</h2>
                {/* Show all movie thumbnails in a genre here */}

                <p> Display movies here</p>


                <div className='movies-display'>
                    {movies.map(movie => (
                        <MovieCard key={movie.movie_id} movie={movie} />
                    ))}
                </div>
            </main>
            

            <Footer />
        </div>
    );
}

export default MoviesDisplay;