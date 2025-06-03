
// Holds Auth provider for react context

import React, {createContext, useState, useEffect} from 'react';
import {useNavigate} from 'react-router-dom';
import axios from 'axios';

export const AuthContext = createContect('AuthContext');
export const AuthProvider = ({children});

    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(null);
    const navigate = useNavigate();

    useEffect => {
        const fetchUser = async () => {
            try {
                const response = await axios.get('/api/auth/user');
                setUser(response.data);
            } catch (error) {
                console.error("Failed to fetch user:", error);
                setUser(null);
            } finally {
                setLoading(false);

            }
            }
            
        
            fetchUser();
        }, [];

        return (
            <AuthContext.Provider value = {{ user, setUser, loading, setLoading, navigate}}>
                {children}
                
            </AuthContext.Provider>
        )

    
