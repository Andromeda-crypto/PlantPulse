import React from 'react';
import { Navigate } from 'react-router-dom';
import ZoomForm from './components/ZoomForm';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import SignupForm from './components/SignupForm';
import QueryForm from './components/QueryForm';
import HomeForm from './components/HomeForm';
import PhotoForm from './components/PhotoForm';
import { AuthProvider } from './auth/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import './App.css';

function App() {
  return (
   
      <Router>
         <AuthProvider>
        <div className="App">
          <Routes>
            <Route path="/" element={<Navigate to="/signup" />} />
            <Route path="/signup" element={<SignupForm />} />
            <Route path="/login" element={<LoginForm />} />
            {/* Protected routes */}
            <Route element={<PrivateRoute />}>
              <Route path="/zoom" element={<ZoomForm />} />
              <Route path="/query" element={<QueryForm />} />
              <Route path="/photo" element={<PhotoForm />} />
              <Route path="/home" element={<HomeForm />} />
            </Route>
          </Routes>
        </div>
        </AuthProvider>
      </Router>
    
  );
}

export default App;

// This is the main application file that sets up the routing for the application.
// It uses React Router to define different routes for the application.
// The AuthProvider wraps the entire application to provide authentication context.
// The Switch component is used to render the first matching route.
// The PrivateRoute component is used to protect certain routes that require authentication.
// The LoginForm, SignupForm, ZoomForm, QueryForm, HomeForm, and PhotoForm components are imported and rendered based on the route.
// The App component is exported as the default export of the module.
// The App component is the main entry point of the React application.
// It sets up the routing and provides the authentication context to all components.
// The App component uses the BrowserRouter from React Router to enable client-side routing.
// The App component imports the necessary components and styles for the application.
// The App component uses the Switch component to render different components based on the current route.
// The App component is the main component that ties everything together in the React application.
// The App component is the main entry point of the React application.
// It sets up the routing and provides the authentication context to all components.
// The App component uses the BrowserRouter from React Router to enable client-side routing.
// The App component imports the necessary components and styles for the application.
// The App component uses the Switch component to render different components based on the current route. 


