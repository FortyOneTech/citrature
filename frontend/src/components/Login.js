import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const Login = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [googleLoaded, setGoogleLoaded] = useState(false);

  useEffect(() => {
    // Load Google Identity Services
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      setGoogleLoaded(true);
    };
    document.head.appendChild(script);

    return () => {
      // Cleanup
      const existingScript = document.querySelector('script[src="https://accounts.google.com/gsi/client"]');
      if (existingScript) {
        document.head.removeChild(existingScript);
      }
    };
  }, []);

  const handleGoogleResponse = useCallback(async (response) => {
    setLoading(true);
    setError('');

    try {
      // Send the ID token to our backend
      const authResponse = await axios.post('/auth/google', {
        id_token: response.credential
      });

      // Store token
      localStorage.setItem('token', authResponse.data.access_token);
      
      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${authResponse.data.access_token}`;
      
      // Get user info
      const userResponse = await axios.get('/auth/me');
      onLogin(userResponse.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  }, [onLogin]);

  useEffect(() => {
    if (googleLoaded && window.google) {
      // Initialize Google Sign-In
      window.google.accounts.id.initialize({
        client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
        callback: handleGoogleResponse,
        auto_select: false,
        cancel_on_tap_outside: true
      });

      // Render the button
      window.google.accounts.id.renderButton(
        document.getElementById('google-signin-button'),
        {
          theme: 'outline',
          size: 'large',
          width: 300,
          text: 'signin_with',
          shape: 'rectangular'
        }
      );
    }
  }, [googleLoaded, handleGoogleResponse]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-indigo-100">
            <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to Citrature
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            AI-powered research paper analysis and citation graphs
          </p>
        </div>

        <div className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm text-center">
              {error}
            </div>
          )}

          {loading && (
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          )}

          <div className="space-y-4">
            <div id="google-signin-button" className="w-full"></div>
            
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">Secure authentication</span>
              </div>
            </div>

            <div className="text-center">
              <p className="text-xs text-gray-500">
                By signing in, you agree to our Terms of Service and Privacy Policy.
                Your data is protected with enterprise-grade security.
              </p>
            </div>
          </div>
        </div>

        {/* Fallback for development */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <h3 className="text-sm font-medium text-yellow-800 mb-2">Development Mode</h3>
            <p className="text-xs text-yellow-700">
              Make sure to set REACT_APP_GOOGLE_CLIENT_ID in your .env file
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;
