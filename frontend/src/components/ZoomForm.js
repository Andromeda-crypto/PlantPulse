import React, { useState } from 'react';

export default function ZoomForm() {
  const [startHour, setStartHour] = useState('');
  const [endHour, setEndHour] = useState('');
  const [plotHtml, setPlotHtml] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch('http://localhost:5000/zoom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
    } catch {
      setError('Something went wrong.');
      setPlotHtml(null);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="zoom-form">
        <input
          type="number"
          placeholder="Start Hour"
          value={startHour}
          onChange={(e) => setStartHour(e.target.value)}
          required
          min="0"
          max="23"
        />
        <input
          type="number"
          placeholder="End Hour"
          value={endHour}
          onChange={(e) => setEndHour(e.target.value)}
          required
          min="0"
          max="23"
        />
        <button type="submit">Zoom</button>
      </form>

      {error && <p className="error-message">{error}</p>}

      {plotHtml && (
        <div
          className="plot-container"
          dangerouslySetInnerHTML={{ __html: plotHtml }}
        />
      )}
    </div>
  );
}

