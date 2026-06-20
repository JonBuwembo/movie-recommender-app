import {createContext, useContext} from "react";
import React from 'react';

type AuthContextType = {
    authFetch: (url: string, options?: RequestInit) => Promise<Response>;
    isAuthenticated: Boolean;
    login: (token: string) => void;
    logout: () => void;
    authLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children } : {children: React.ReactNode}) => {

    const [isAuthenticated, setIsAuthenticated] = React.useState(false);
    const [authLoading, setAuthLoading] = React.useState(true);

    const token = localStorage.getItem('token');

    React.useEffect(() => {

        try {
            if (token) {
                setAuthLoading(true);
                const decodedToken = JSON.parse(atob(token.split(".")[1]));
                const isExpired = decodedToken.exp * 1000 < Date.now();

                if (!isExpired) {
                    setIsAuthenticated(true);
                } else {
                    localStorage.removeItem("token")
                }
            }
            setAuthLoading(false);
        } catch (error) {
            console.error("Error with token expiration:", error);
        } finally {
            setAuthLoading(false);
        }
        
        
    }, [token])

    
    const authFetch = async (url: string, options : RequestInit = {}) => {
        const response = await fetch(url, {
            ...options, 
            headers: {
                "Content-Type" : "application/json",
                "Authorization" : `Bearer ${token}`,
                ...options.headers
            }
        })

        // prevents authorized responses from turning into runtime errors.
        if (response.status === 401) {
            alert("Your session has expired. Please log in again.");
            localStorage.removeItem("token");
            setIsAuthenticated(false);
            throw new Error("Unauthorized");
        }

        return response
    }

    const login = (token: string) => {
        localStorage.setItem("token", token);
        setIsAuthenticated(true);    
    }

    const logout = () => {
        localStorage.removeItem("token")
        setIsAuthenticated(false);
    }

    return (
        <AuthContext.Provider value={{authFetch, isAuthenticated, login, logout, authLoading}}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    const context = useContext(AuthContext); 

    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider")
    }

    return context;

}
