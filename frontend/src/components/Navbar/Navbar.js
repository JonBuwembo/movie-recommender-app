import react from 'react';
import './Navbar.css';
import { useNavigate } from 'react-router-dom';
import { useGenre } from '../../GenreContext';
import { Search } from "lucide-react";
import { useSearch } from '../../SearchContext';


const Navbar = () => {

    const {searchQuery, setSearchQuery} = useSearch();
    
    const {setSelectedGenre} = useGenre();
    const navigateTo = useNavigate();

    const [open, setOpen] = react.useState(false);
    const dropdownRef = react.useRef(null);

    // Close dropdown when user clicks outside 
    react.useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setOpen(false); // Close dropdown if click is outside of it
            }
        }

        document.addEventListener('mousedown', handleClickOutside);

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        }
    }, []);


    const toggleDropdown = (e) => {
        e.preventDefault();
        setOpen(!open);
    }

    const handleGenreSelect = (genre) => {
        setSelectedGenre(genre);
        setOpen(false);
        navigateTo(`/genres/${genre}`); // genreParam in app.tsx reads this genre.
    }

    const genres = [
        "Action",
        "Comedy",
        "Drama",
        "Horror",
        "Sci-Fi",
        "Western",
        "Romance",
        "Thriller",
        "Adventure",
        "Musical",
        "Film-Noir",
        "Animation",
        "War"]

    const handleSearchSubmit = (event) => {
        event.preventDefault();
        const query = event.target.search.value;
        if (!query) {
            return;
        }
        
        navigateTo(`/movies/${query}`);
        console.log('Search query:', query);
        // Here you can add logic to handle the search query, e.g., redirecting to a search results page
        setSearchQuery(''); // clear search input after submission
    }

    return (
        <nav>
            <ul>
                <li> <a href="/">Home</a> </li>
                <li className='dropdown' ref={dropdownRef}>

                    <a href="/genres" onClick={toggleDropdown}>Genres</a> 

                    {open &&
                        <ul className='dropdown-menu'>
                            {genres.map(genre => (
                                <li key={genre}> 
                                    <a href={`/genres/${genre}`} 
                                    onClick={
                                        (e) => {
                                            e.preventDefault(); {/* needed so genre can actually be passed up */}
                                            handleGenreSelect(genre);
                                        }
                                    }>
                                        {genre} 
                                    </a>
                                </li>
                            ))}
                        </ul>
                    }
                    
                </li>
                <li> <a href="/movies"> Movies </a> </li>
                <li> <a href="/about">About</a> </li>
            </ul>

            <form className="nav-search" onSubmit={handleSearchSubmit}>
                <div className="search-wrapper">
               
                    <input 
                        className="nav-search-input" 
                        type='text' 
                        name="search" 
                        placeholder="Search movies ..." 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    {/* <button type='submit' className='nav-search-btn'> <Search size={20} /> </button> */}
                </div>
                
            </form>
        </nav>
    );
}

export default Navbar;