// src/components/SignupForm.js
import React, { useState, useContext } from 'react';
import  { AuthContext } from '../auth/AuthContext' ;


export default function SignupForm({ onSignupSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const[ confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const { setUser, setLoading} = useContext(AuthContext)

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      console.log('Sending signup request:', { username, email, password, confirmPassword });
      const res = await fetch('/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password, email, confirm_password: confirmPassword }),
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
      console.error('Signup error:');
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
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        />
      < input 
        type="password"
        placeholder="Confirm Password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
      />
      { password !== confirmPassword && (
        <p className="error-message">Passwords do not match</p>
      )}
      <button type="submit">Sign Up</button>
      {error && <p className="error-message">{error}</p>}
    </form>
  );
}



