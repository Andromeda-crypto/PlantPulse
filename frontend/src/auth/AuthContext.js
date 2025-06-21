// Holds Auth provider for React context

import React, { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';




export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true); 
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await axios.get('http://localhost:5000/api/auth/user');
                setUser(response.data);
            } catch (error) {
                console.error("Failed to fetch user:", error);
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        fetchUser();
    }, []);

    return (
        <AuthContext.Provider value={{ user, setUser, loading, setLoading, navigate }}>
            {children}
        </AuthContext.Provider>
    );
    
};

// The AuthProvider component fetches the user data from the server when it mounts.
// It provides the user data, loading state, and a function to set the user in the context.
// The context can be used in other components to access the authentication state and user data.
// The useNavigate hook is used to programmatically navigate to different routes.
// This is useful for redirecting users after login or logout actions.
// The AuthContext can be used in other components to access the authentication state and user data.
// The AuthProvider component wraps the application and provides the authentication context to all components.
// This allows components to access the user data and loading state without prop drilling.
// The AuthContext is created using React's createContext API.
// The AuthProvider component uses the useEffect hook to fetch the user data when it mounts.
// The useState hook is used to manage the user and loading state.
// The axios library is used to make HTTP requests to the server to fetch user data.
// The AuthProvider component can be used in the main application file to wrap the entire app.


    
