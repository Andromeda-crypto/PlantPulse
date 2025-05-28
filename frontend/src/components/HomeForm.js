// src/compoonents/HomeForm.js
import React, { useState } from 'react';


export default function HomeForm({ onHomeSuccess}) {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
        const res = await fetch('http://localhost:5000/home', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password }),
        });
        const data = await res.json();
        if (res.ok) {
            setError(null);
            if (onHomeSuccess) {
               onHomeSuccess(data);
        };
        } else {
            setError(data.error || 'Home request failed');
        }
        } catch (err) {
            console.error(err);
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
        <button type="submit">Home</button>
        {error && <p className="error-message">{error}</p>}
        </form>
    );
}

