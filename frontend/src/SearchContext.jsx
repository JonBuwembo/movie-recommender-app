import React, { createContext, useContext, useState } from "react";

const SearchContext = createContext();

export const SearchProvider = ({children}) => {
    const [searchQuery, setSearchQuery] = React.useState("");

    return (
        <SearchContext.Provider value={{searchQuery, setSearchQuery}}>
            {children}
        </SearchContext.Provider>
    )
}

export const useSearch = () => {
    const context = useContext(SearchContext);
    return context;
}