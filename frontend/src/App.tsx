import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import logo from './logo.svg';
import './styles/global.css';
import LandingPage from './pages/LandingPage';
import ResultsPage from './pages/ResultsPage';
import MoviesDisplay from './pages/MoviesDisplay';
import About from './pages/About';
import { GenreProvider } from './GenreContext';

function App() {
  return (
    <>
      {/* Home page will be the LandingPage.js */}
      <GenreProvider>
        <Router>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/movies" element={<MoviesDisplay />} />
            <Route path='/about' element={<About />} />
            <Route path='/genres/:genreParam?' element={<MoviesDisplay />} />
          </Routes>
        </Router>
      </GenreProvider>

    </>
  );
}

export default App;
