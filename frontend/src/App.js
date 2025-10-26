import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import Landing from './components/Landing';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import CollectionView from './components/CollectionView';
import './App.css';

// Configure axios defaults
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
axios.defaults.withCredentials = true;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Check if we have a stored token
      const token = localStorage.getItem('token');
      if (token) {
        // Set the authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // Verify the token is still valid
        const response = await axios.get('/auth/me');
        setUser(response.data);
      } else {
        setUser(null);
      }
    } catch (error) {
      // Token is invalid, clear it
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await axios.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear token and authorization header
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route
            path="/"
            element={<Landing />}
          />
          <Route
            path="/login"
            element={
              user ? <Navigate to="/dashboard" replace /> : <Login onLogin={handleLogin} />
            }
          />
          <Route
            path="/dashboard"
            element={
              user ? (
                <Dashboard user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/collection/:id"
            element={
              user ? (
                <CollectionView user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
