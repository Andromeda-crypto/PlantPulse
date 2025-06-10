// src/components/LoginForm.js
import React, { useContext, useState } from 'react';
import {AuthContext} from '../auth/AuthContext';


export default function LoginForm({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const { setUser, setLoading} = useContext(AuthContext)
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log('Sending login requests:',{username, password});
      const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      console.log('Received response:', res);
      console.log('Response data:', data);
      if (res.ok) {
        setUser({ username: data.username });
        setLoading(false);
        if (onLoginSuccess) {
          onLoginSuccess(data);
        }
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      console.error('Network or server error:', err)
      setError('Network error');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
      />
      <button type="submit">Log In</button>
      {error && <p className="error-message">{error}</p>}
    </form>
  );
}
