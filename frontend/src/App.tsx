import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import logo from './logo.svg';
import './styles/global.css';
import LandingPage from './pages/LandingPage';
import ResultsPage from './pages/ResultsPage';
import MoviesDisplay from './pages/MoviesDisplay';
import About from './pages/About';

function App() {
  return (
    <>
      {/* Home page will be the LandingPage.js */}
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/movies" element={<MoviesDisplay />} />
          <Route path='/about' element={<About />} />
        </Routes>
      </Router>

    </>
  );
}

export default App;
