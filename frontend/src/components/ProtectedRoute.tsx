
import { Navigate } from "react-router-dom";
import React from "react";


const ProtectedRoute = ({children} : { children: React.ReactNode }) => {

    const user = localStorage.getItem('user');

    if (!user) {
        return <Navigate to="/" replace />
    }

    return <>{children}</>;
}

export default ProtectedRoute;