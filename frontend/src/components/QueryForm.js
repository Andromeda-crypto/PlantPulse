// src/components/QueryForm.js

import React, {useState} from 'react';

export default function QueryForm() {
    const [query, setQuery] = useState('');
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);

    consthandleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch('https://localhost:5000/query', {
                method : 'POST',
                headers : { 'Content-Type': 'application/json'},
                credentials : 'include',
                body: JSON.stringify({query}),
});
            const data = await res.json();

            if (res.ok) {
                setError(null);
                setResult(data.result);
                if (onQuerySuccess) {
                    onQuerySuccess(data);
                };
            } else {
                setError(data.error || "Query request failed");;
            }
            } catch (err) {
                console.error(err);
                setError("Network error");
            }
      }
    };

    // Render the form and result

    return (
        <div>
            <form onSubmit={handleSubmit} className="query-form">
                <input 
                type = "text" 
                placehoder="Enter Start Time"
                value={query}
                onChange= {(e) => setQuery(e.target.value)}
                required
                />
               
                </form>

            <form onUbmit={handleSubmit} className="query-form">
                <input
                type="number"
                placeholder="Enter End Time"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                required
                />
                </form> 

                <button type="submit">Go</button>               
                       </div>
    )


    