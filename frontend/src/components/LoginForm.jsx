import React, { useState } from 'react';
import axios from 'axios';
import './LoginForm.css'; 

export default function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/token/', {
        username,
        password,
      });

      const access = res.data.access;
      localStorage.setItem('access', access);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      onLogin();
    } catch (err) {
      setError('Credenciales incorrectas. Intenta de nuevo.');
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-box">
        <h2>Iniciar sesión</h2>

        <label htmlFor="username">Username:</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <label htmlFor="password">Password:</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit">Entrar</button>

        {error && <p className="error">{error}</p>}

        <p style={{ marginTop: '16px' }}>
          <a href="http://127.0.0.1:8000/" style={{ color: '#007bff', textDecoration: 'none' }}>
            ← Volver al Backend
          </a>
        </p>

      </form>
    </div>
  );
}
