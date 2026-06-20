import { FaStar } from 'react-icons/fa'
import { useState, useEffect } from 'react';
import '../../styles/movieDetails.css';
import { useAuth } from '../../AuthContext';
import config from '../../config';

const StarRating = ({ movieId }) => {

    const [rating, setRating] = useState(0);
    const [hoverValue, setHoverValue] = useState(undefined);

    const {authFetch} = useAuth();

    useEffect(() => {
        
        // fetch rating for this current movie
        const fetchRating = async (movieId) => {
            try {
            
                const response = await authFetch(`${config.API_URL}/api/rating/${movieId}`)
                .catch(error => {
                    if(error.message === "Unauthorized") {
                        return;
                    }

                    console.error(error)
                });

                const data = await response.json();

                if (!response.ok) {
                    console.error("Failed to retrieve rating for this movie");
                    return;
                }

                if (data?.rating) setRating(data.rating);

            } catch (error) {
                console.error("Error fetching rating: ", error);
            }
        }

        fetchRating(movieId)

    }, [movieId, authFetch])

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
            const response = await authFetch(`${config.API_URL}:5000/api/rating`, {
                method: "POST",
                body: JSON.stringify({
                    movieId: movieId,
                    rating: value
                })
            })

            if (!response.ok) {
                console.error("failed to update/send rating")
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
                    onMouseOver={() => handleMouseOverStar(index + 1)}
                    onMouseLeave={() => handleMouseLeaveStar()}
                />
            )
       })}
    </div>
    );
}

export default StarRating;