import react from 'react';
import './Navbar.css';
import { useNavigate, useParams } from 'react-router-dom';
import { useGenre } from '../../GenreContext';
import { useSearch } from '../../SearchContext';
import { Clapperboard, Film, Search, House, LogOut, Bookmark, Bot, BookA } from "lucide-react";
import { useAuth } from '../../AuthContext';
import { Link } from 'react-router-dom';


const Navbar = () => {

    const {searchQuery, setSearchQuery} = useSearch();
    
    const {setSelectedGenre} = useGenre();
    const navigateTo = useNavigate();

    const {logout} = useAuth();

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
        const query = event.target.search.value.trim();
        if (!query) {
            return;
        }
        
        navigateTo(`/movies/search/${query}`);
        console.log('Search query:', query);
        // Here you can add logic to handle the search query, e.g., redirecting to a search results page
        setSearchQuery(''); // Clear the search input after submission
    }

    const signOut = (event) => {
        event.preventDefault();
        logout()
        navigateTo("/");
    }

    return (
        <nav className="navbar">

            <div className="nav-left">
                
                <a className='logo' href="/home">
                    🎬 MidnightScoop
                </a>

                <ul className='nav-links'>
                    <li> <Link to="/home" className="nav-link"> <House size={20} /> Home</Link> </li>
                    <li className='dropdown' ref={dropdownRef}>

                        <Link className="nav-link" to="/genres" onClick={toggleDropdown}>
                            <Film size={20} /> 
                            Genres
                        </Link> 


                        
                            {open &&
                                <ul className='dropdown-menu'>
                                    {genres.map(genre => (
                                        <li key={genre}> 
                                            <Link to={`/genres/${genre}`} className="nav-link"
                                            onClick={
                                                (e) => {
                                                    e.preventDefault(); {/* needed so genre can actually be passed up */}
                                                    handleGenreSelect(genre);
                                                }
                                            }>
                                                {genre} 
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            }
                        
                        
                    </li>

                    <li> 
                        <Link to="/movies" className="nav-link"> 
                            <Clapperboard size={20} /> 
                            Movies 
                        </Link> 
                    </li>
                    <li> <Link to="/about" className="nav-link"> <BookA size={20} /> About</Link> </li>
                    
                    <li> <Link to="/movies/ask" className="nav-link"> <Bot size={20} /> Ask</Link></li>
                </ul>
            </div>

            

            
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

            <div className='nav-right'>
                <li> <Link to="/movies/watchlist" className="nav-link"> <Bookmark size={20} />Watchlist</Link></li>

                <button className="signout-btn" onClick={signOut}>
                    <LogOut size={20} />
                    Sign Out
                </button>
            </div>

        </nav>
    );
}

export default Navbar;