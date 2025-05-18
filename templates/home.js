import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LoginSignup() {
  const navigate = useNavigate();

  // Toggle between login and signup view
  const [isLogin, setIsLogin] = useState(true);

  // Shared form fields
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState(''); // for signup only
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState(''); // for signup only

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const url = isLogin ? '/login' : '/signup';
    const payload = isLogin
      ? { username, password }
      : { username, email, password, confirm_password: confirmPassword };

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok && data.success !== false) {
        // Redirect to /home on success
        navigate('/home');
      } else {
        setError(data.message || data.error || 'Something went wrong');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">
        {isLogin ? 'Login to PlantPulse' : 'Create a PlantPulse Account'}
      </h2>

      {error && (
        <div className="mb-4 p-2 bg-red-200 text-red-800 rounded">{error}</div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block mb-1 font-semibold">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        {!isLogin && (
          <div className="mb-4">
            <label className="block mb-1 font-semibold">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required={!isLogin}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
        )}

        <div className="mb-4">
          <label className="block mb-1 font-semibold">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        {!isLogin && (
          <div className="mb-4">
            <label className="block mb-1 font-semibold">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required={!isLogin}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition"
        >
          {loading ? (isLogin ? 'Logging in...' : 'Signing up...') : (isLogin ? 'Login' : 'Sign Up')}
        </button>
      </form>

      <p className="mt-4 text-center">
        {isLogin ? (
          <>
            Don't have an account?{' '}
            <button
              className="text-green-600 font-semibold hover:underline"
              onClick={() => {
                setError(null);
                setIsLogin(false);
              }}
            >
              Sign up here
            </button>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <button
              className="text-green-600 font-semibold hover:underline"
              onClick={() => {
                setError(null);
                setIsLogin(true);
              }}
            >
              Login here
            </button>
          </>
        )}
      </p>
    </div>
  );
}
