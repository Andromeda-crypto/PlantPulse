// This is a simple React application that allows users to input start and end hours
// for zooming in on a plot. It sends the input to a Flask backend and displays the resulting plot.

import React, { useState } from 'react';

function App() {
  const [startHour, setStartHour] = useState('');
  const [endHour, setEndHour] = useState('');
  const [plotHtml, setPlotHtml] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    
    try {
      const res = await fetch('http://localhost:5000/zoom', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ start_hour: startHour, end_hour: endHour }),
      });

      const data = await res.json();

      if (res.ok) {
        setPlotHtml(data.plot_html);
        setError(null);
      } else {
        setError(data.error);
        setPlotHtml(null);
      }
    } catch (err) {
      setError('Something went wrong.');
      setPlotHtml(null);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Zoom View</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          placeholder="Start Hour"
          value={startHour}
          onChange={(e) => setStartHour(e.target.value)}
        />
        <input
          type="number"
          placeholder="End Hour"
          value={endHour}
          onChange={(e) => setEndHour(e.target.value)}
        />
        <button type="submit">Zoom</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {plotHtml && (
        <div
          dangerouslySetInnerHTML={{ __html: plotHtml }}
          style={{ marginTop: '2rem', border: '1px solid #ccc', padding: '1rem' }}
        />
      )}
    </div>
  );
}

export default App;




