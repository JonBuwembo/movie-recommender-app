
import { Navigate } from "react-router-dom";
import React from "react";
import { useAuth } from "../AuthContext";


const ProtectedRoute = ({children} : { children: React.ReactNode }) => {

    const { isAuthenticated, authLoading} = useAuth();

    if (authLoading) return <p> loading ... </p>
    if (!isAuthenticated) {
        return <Navigate to="/" replace />
    }

    return <>{children}</>;
}

export default ProtectedRoute;