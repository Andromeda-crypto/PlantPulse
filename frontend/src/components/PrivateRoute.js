// PrivateRoute.jsx
import React, { useContext, useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { AuthContext } from '../auth/AuthContext';
import axios from 'axios';

const PrivateRoute = () => {
    const { user, loading, setUser } = useContext(AuthContext);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await axios.get('/api/auth/user'); // prefix with slash
                setUser(response.data); // optional if context supports it
            } catch (error) {
                console.error("Failed to fetch user:", error);
            }
        };

        fetchUser();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    return user ? <Outlet /> : <Navigate to="/login" />;
};

export default PrivateRoute;
// This component checks if the user is authenticated before allowing access to certain routes.
// If the user is not authenticated, it redirects them to the login page.
// If the user is authenticated, it renders the child components using <Outlet />.