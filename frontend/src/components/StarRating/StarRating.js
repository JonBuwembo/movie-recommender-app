import { FaStar } from 'react-icons/fa'
import { useState } from 'react';
import '../../styles/movieDetails.css';

const StarRating = ({ movieId }) => {

    const [rating, setRating] = useState(0);
    const [hoverValue, setHoverValue] = useState(undefined);

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
            await fetch("/api/rating"), {
                method: "POST",
                headers: {
                    "Content-Type" : "application/json"
                },
                body: JSON.stringify({
                    movieId,
                    rating: value
                })
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