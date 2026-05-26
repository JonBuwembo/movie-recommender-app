import MovieCard from "../components/MovieCard/MovieCard";
import { VirtuosoGrid } from "react-virtuoso";

const COLUMN_COUNT = 5;
const CARD_WIDTH = 250;
const CARD_HEIGHT = 420;

const VirtualMovieGrid = ({ movies = [], mode = "normal" }) => {

    return (
        <div className="movies-display">

            <VirtuosoGrid
                data={movies}
                listClassName="movies-display"
                components={{
                    Item: ({ children, ...props }) => (
                        <div {...props}>
                            {children}
                        </div>
                    )
                }}

                itemContent={(index, movie) => (
                    <MovieCard movie={movie} mode={mode} />
                )}
             />
        </div>
    );
};

export default VirtualMovieGrid;