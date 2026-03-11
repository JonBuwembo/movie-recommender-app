import react from 'react';
import './Navbar.css';

const Navbar = () => {

    const handleSubmit = (event) => {
        event.preventDefault();
        const query = event.target.search.value;
        console.log('Search query:', query);
        // Here you can add logic to handle the search query, e.g., redirecting to a search results page
    }

    return (
        <nav>
            <ul>
                <li> <a href="/">Home</a> </li>
                <li> <a href="/genres">Genres</a> </li>
                <li> <a href="/movies"> Movies </a> </li>
                <li> <a href="/about">About</a> </li>
            </ul>

            <form className="nav-search" onSubmit={handleSubmit}>
                <input className="nav-search-input" type='text' name="search" placeholder="Search movies ..." />
                <button type='submit' className='nav-search-btn'> <i className="fas fa-search"></i> </button>
            </form>
        </nav>
    );
}

export default Navbar;