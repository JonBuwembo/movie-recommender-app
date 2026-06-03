import { FaStar } from 'react-icons/fa'
import { useState, useEffect } from 'react';
import '../../styles/movieDetails.css';
import { useAuth } from '../../AuthContext';

const StarRating = ({ movieId }) => {

    const [rating, setRating] = useState(0);
    const [hoverValue, setHoverValue] = useState(undefined);

    const {authFetch} = useAuth();

    const userId = JSON.parse(localStorage.getItem('user') || "null");

    useEffect(() => {
        
        // fetch rating for this current movie
        const fetchRating = async (movieId) => {
            try {
            
                const response = await authFetch(`http://localhost:5000/api/rating/${movieId}`);
                const data = await response.json();

                if (!response.ok) {
                    console.error("Failed to retrieve rating for this movie");
                    return;
                }

                if (data.rating) setRating(data.rating);

            } catch (error) {
                console.error("Error fetching rating: ", error);
            }
        }

        fetchRating(movieId)

    }, [movieId])

    const handleMouseOverStar = (value) => {
        setHoverValue(value)
    }

    const handleMouseLeaveStar = () => {
        setHoverValue(undefined)
    }

    const handleClickStar = async (value) => {
        setRating(value)

        try {
            // api endpoint not yet setup, but table is created
            const response = await authFetch("http://localhost:5000/api/rating", {
                method: "POST",
                body: JSON.stringify({
                    movieId: movieId,
                    rating: value
                })
            })

            if (!response.ok) {
                console.error("failed to update/send rating")
            } else {
                console.log( await response.json())
            }

        } catch (error) {
            console.log("Error sending rating: ", error)
        }
    }
    const colors = {
        orange: "#93b10d",
        grey: "f8f8ff"
    }

    const stars = Array(5).fill(0);

    return (
    <div className="stars">
       {stars.map((_, index) => {
            return (
                <FaStar
                    key={index}
                    size={25}
                    value={rating}
                    onChange={(e) => setRating(e.target.value)}
                    color={(hoverValue || rating) > index ? colors.orange : colors.grey}
                    onClick={() => handleClickStar(index + 1)} 
                    onMouseHover={() => handleMouseOverStar(index + 1)}
                    onMouseLeave={() => handleMouseLeaveStar()}
                />
            )
       })}
    </div>
    );
}

export default StarRating;