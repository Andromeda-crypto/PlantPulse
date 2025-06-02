import React from 'react';
import ZoomForm from './components/ZoomForm';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import SignupForm from './components/SignupForm';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute'; 
import QueryForm from './components/QueryForm';
import HomeForm from './components/HomeForm';
import PhotoForm from './components/PhotoForm';
import './App.css';

function App() {
  return (
    <div className="App">
      <h2>Home</h2>
      <HomeForm />
    </div>
  );
}

export default App;

