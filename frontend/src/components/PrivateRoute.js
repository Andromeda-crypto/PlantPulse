// src/components/PrivateRoute.js
import React, { useContext, useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import  {AuthContext} from '.src/auth/AuthContext.js'

import axios from 'axios';

const PrivateRoute = () => {
  const { user, loading, setUser, setLoading } = useContext(AuthContext);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get('/api/auth/user');
        setUser(response.data);
      } catch (error) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    // Only fetch if loading is true and user is null
    if (loading && user === null) {
      fetchUser();
    }
  }, [loading, user, setUser, setLoading]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return user ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;

// This component checks if the user is authenticated before rendering the child components.
// If the user is authenticated, it renders the child components using <Outlet />.  
// If the user is not authenticated, it redirects to the login page using <Navigate />.
// The useEffect hook is used to fetch the user data from the server when the component mounts.
// The axios library is used to make the HTTP request to fetch the user data.
// The loading state is used to show a loading message while the user data is being fetched.
// The AuthContext is used to access the user data and loading state.
// The component uses the useContext hook to access the AuthContext.
// The component returns a loading message while the user data is being fetched.
// If the user is authenticated, it renders the child components using <Outlet />.
// If the user is not authenticated, it redirects to the login page using <Navigate />.
// The component is exported as the default export of the module.
// This component is used to protect routes that require authentication.
// It ensures that only authenticated users can access certain parts of the application.
// The component can be used in the main application file to wrap protected routes.
// The component can be used in the main application file to wrap protected routes.
