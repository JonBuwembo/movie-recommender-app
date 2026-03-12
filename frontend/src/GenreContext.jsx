import React, {createContext, useContext, useState} from 'react';

const GenreContext = createContext();

export const GenreProvider = ({ children }) => {
    const [selectedGenre, setSelectedGenre] = useState();

    return (
        <GenreContext.Provider value={{ selectedGenre, setSelectedGenre}} >
            {children}
        </GenreContext.Provider>
    )
};

export const useGenre = () => {
    const context = useContext(GenreContext);
    return context;
}