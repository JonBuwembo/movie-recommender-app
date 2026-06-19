import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import logo from './logo.svg';
import './styles/global.css';
import LandingPage from './pages/LandingPage';
import ResultsPage from './pages/ResultsPage';
import MoviesDisplay from './pages/MoviesDisplay';
import About from './pages/About';
import { GenreProvider } from './GenreContext';
import MovieDetails from './pages/MovieDetails';
import Register from './pages/Register';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';
import ChatStartSceen from './pages/ChatStartScreen';

function App() {
  return (
    <>
      {/* Home page will be the LandingPage.js */}
      <GenreProvider>
        <Router>
          <Routes>

            <Route path="/" element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            } />

            <Route path="/register" element={
              <PublicRoute>
                <Register />
              </PublicRoute>
            } />

            {/* Routes below should only be accessible after the user logs in. */}
            <Route path="/home" element={
              <ProtectedRoute> 
                <LandingPage /> 
              </ProtectedRoute>
            } />

            <Route path="/results" element={
              <ProtectedRoute> 
                <ResultsPage /> 
              </ProtectedRoute>
            } />

            <Route path="/movies" element={
              <ProtectedRoute> 
                <MoviesDisplay /> 
              </ProtectedRoute> 
            } />

            <Route path='/movies/search/:queryParam?' element={
              <ProtectedRoute> 
                <MoviesDisplay /> 
              </ProtectedRoute> } />

            <Route path='/movies/watchlist' element={
              <ProtectedRoute> 
                <MoviesDisplay /> 
              </ProtectedRoute> 
            } />

            <Route path='/movies/details/:movieIdParam?' element={
              <ProtectedRoute> 
                <MovieDetails /> 
              </ProtectedRoute> 
            } />

            <Route path='/genres/:genreParam?' element={
              <ProtectedRoute> 
                <MoviesDisplay /> 
              </ProtectedRoute> } />

            <Route path='/about' element={
              <ProtectedRoute> 
                <About /> 
              </ProtectedRoute> 
            } />

            <Route path='/movies/ask' element = {
              <ProtectedRoute>
                <ChatStartSceen />
              </ProtectedRoute>
            } />            
            
          </Routes>
        </Router>
      </GenreProvider>

    </>
  );
}

export default App;
