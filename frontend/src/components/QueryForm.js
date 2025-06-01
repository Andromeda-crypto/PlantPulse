// src/components/QueryForm.js

import React, { useState } from 'react';

export default function QueryForm({ onQuerySuccess }) {
    const [startTime, setStartTime] = useState('');
    const [endTime, setEndTime] = useState('');
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch('http://localhost:5000/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ start_time: startTime, end_time: endTime }),
            });
            const data = await res.json();

            if (res.ok) {
                setError(null);
                setResult(data.result);
                if (onQuerySuccess) {
                    onQuerySuccess(data);
                }
            } else {
                setError(data.error || "Query request failed");
            }
        } catch (err) {
            console.error(err);
            setError("Network error");
        }
    };

    return (
        <div className="query-container">
            <form onSubmit={handleSubmit} className="query-form">
                <input
                    type="text"
                    placeholder="Enter Start Time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    required
                />
                <input
                    type="text"
                    placeholder="Enter End Time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    required
                />
                <button type="submit">Go</button>
            </form>

            {error && <p className="error-message">{error}</p>}

            {result && (
                <div className="query-result">
                    <h3>Query Result:</h3>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}

    

  

