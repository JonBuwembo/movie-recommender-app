import react from 'react';  
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';
import '../styles/global.css';

const About = () => {

    return (
        <div className='layout'> 
            <Navbar />
            

            <main>
                <h2>About Page</h2>

                {/* Add information about the application here */}
                <p className= "about-explanation"> 
                    This application provides movie recommendations based on your preferences. Explore different genres, search for your favorite movies, and discover new ones tailored just for you. 
                    
                    Whether you're a fan of classics or modern films, our collection has something for everyone. Happy watching!
                </p>
            </main>

            <Footer />
        </div>
    );
}

export default About;