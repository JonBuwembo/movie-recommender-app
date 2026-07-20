import Navbar from '../components/Navbar/Navbar';
import '../styles/global.css';
import '../styles/about.css';

const About = () => {

    return (
        <div className="about-page"> 
            <Navbar />
            <div className="about-wrapper">
                
                {/* BACKGROUND VIDEO (FIRST LAYER) */}
                <video className='bg-video' autoPlay loop muted playsInline>
                    <source src="/videos/movie-bg-about.mp4" type="video/mp4" />
                </video>

                {/* DARK OVERLAY (2ND layer) */}
                <div className="overlay" />

                {/* CONTENT (top layer) */}
                <main className='all-content'>
                     <section className="about-hero">
                        <h2>Find your next favorite movie in seconds</h2>
                        <p>
                            This app learns your taste and turns endless scrolling into focused discovery on classic cinema, early 2000s favorites, and timeless storytelling.
                        </p>
                    </section>

                    <section className='about-section'>
                        <h3> What it does</h3>
                        <p>
                            This is a personalized movie discovery platform designed to help you explore films that match your interests. Explore handpicked classics, early 2000s gems, and timeless films tailored to your preferences.
                        </p>
                    </section>

                    <section className='about-section'>
                        <h3> Why it works</h3>
                        <p> 
                            Instead of overwhelming you with every possible title, the system focuses on curated dataset of meaningful films. By combining user behavior with structured recommendations, it highlights movies you're more likely to actually enjoy.
                        </p>
                    </section>

                    <section className='about-section'>
                        <h3> Features </h3>
                        <ul>
                            <li>AI-powered movie recommendations</li>
                            <li>Personalized user profiles</li>
                            <li>Watchlist to save movies for later </li>
                            <li> Fast search across genres and titles </li>
                            <li> Rating system to refine suggesions</li>
                        </ul>
                    </section>

                    <section className='about-hero'>
                        <p> Built for discovering films already passed the test of time.</p>
                    </section>
                </main>

            </div>
        </div>
    );
}

export default About;