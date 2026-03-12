import react, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/global.css';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import MovieCard from '../components/MovieCard/MovieCard';
import '../styles/movies.css';
import {useGenre } from '../GenreContext';

const MoviesDisplay = () => {
    const {genreParam} = useParams(); //read url for other pages
    console.log('Genre param from URL:', genreParam);

    const [displayedMovies, setDisplayedMovies] = react.useState([]);

    //const [selectedGenre, setSelectedGenre] = react.useState(null);
    const {selectedGenre, setSelectedGenre} = useGenre();

    const [loading, setLoading] = react.useState(false);

    const fetchMovies = (genre) => {
        setLoading(true);
        console.log('Fetching movies for genre:', genre);
        const fetchURL = genre ? `http://localhost:5000/api/movies/${genre}` : 'http://localhost:5000/api/movies';

        fetch(fetchURL)
            .then(response => response.json())
            .then(data => {
                setDisplayedMovies(data);
                setSelectedGenre(genre);
                setLoading(false);
            })
            .catch(error =>{
                console.error('Error fetching movies:', error);
                setDisplayedMovies([]);
                setSelectedGenre(genre);
                setLoading(false);
            });
    };

    useEffect(() => {
        if (genreParam) {
            console.log('Fetching movies for genre:', genreParam);
            fetchMovies(genreParam);
        } else {
            fetchMovies(null);
        }
    }, [genreParam]);

    return (
        <div className='layout'>
            <Navbar />
            
            <main>
                {selectedGenre ? 
                        <h2> Movies in {selectedGenre} genre </h2> 
                        : <h2> Browse your favorite vintage movies here! </h2>
                }
                {/* Show all movie thumbnails in a genre here otherwise all movies */}

                <div className='movies-display'>
                   {loading ? (
                       <p>Loading movies... </p> // Show while fetching
                    ) : displayedMovies.length > 0 ? (
                        displayedMovies.map(movie => <MovieCard key={movie.movie_id} movie={movie} />)
                    ) : selectedGenre ? (
                        <p>No movies found for {selectedGenre}.</p>
                    ) : (
                        <p>No movies available.</p>
                    )}
                </div>
            </main>
            

            <Footer />
        </div>
    );
}

export default MoviesDisplay;