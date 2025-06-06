// src/components/SignupForm.js
import React, { useState, useContext } from 'react';
import  { AuthContext } from '../auth/AuthContext' ;


export default function SignupForm({ onSignupSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const { setUser, setLoading} = useContext(AuthContext)

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch('http://localhost:5000/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (res.ok) {
        setError(null);
        if (onSignupSuccess) {
          onSignupSuccess(data);
        }
      } else {
        setError(data.error || 'Signup failed');
      }
    } catch (err) {
      
      setError('Network error');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <input
        type="text"
        placeholder="username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">Sign Up</button>
      {error && <p className="error-message">{error}</p>}
    </form>
  );
}


