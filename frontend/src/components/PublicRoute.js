import { Navigate } from "react-router-dom";
import React from "react";
import { useAuth } from "../AuthContext";

// Skip logins/signups if token is still active.

const PublicRoute = ({children}) => {
    const {isAuthenticated} = useAuth();
    return isAuthenticated ? <Navigate to="/home" /> : children;
}

export default PublicRoute;