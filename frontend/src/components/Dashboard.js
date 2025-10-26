import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Plus, BookOpen, LogOut, Home } from 'lucide-react';

const Dashboard = ({ user, onLogout }) => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      const response = await axios.get('/collections/');
      setCollections(response.data);
    } catch (error) {
      console.error('Error fetching collections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCollection = async (e) => {
    e.preventDefault();
    if (!newCollectionName.trim()) return;

    try {
      const response = await axios.post('/collections/', {
        title: newCollectionName
      });
      setCollections([...collections, response.data]);
      setNewCollectionName('');
      setShowCreateForm(false);
    } catch (error) {
      console.error('Error creating collection:', error);
    }
  };

  const handleDeleteCollection = async (id) => {
    if (!window.confirm('Are you sure you want to delete this collection?')) return;

    try {
      await axios.delete(`/collections/${id}`);
      setCollections(collections.filter(c => c.id !== id));
    } catch (error) {
      console.error('Error deleting collection:', error);
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-indigo-600" />
              <h1 className="ml-2 text-2xl font-bold text-gray-900">Citrature</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/"
                className="flex items-center text-sm text-gray-500 hover:text-gray-700"
              >
                <Home className="h-4 w-4 mr-1" />
                Home
              </Link>
              <span className="text-sm text-gray-500">Free Plan</span>
              <button
                onClick={onLogout}
                className="flex items-center text-sm text-gray-500 hover:text-gray-700"
              >
                <LogOut className="h-4 w-4 mr-1" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Your Collections</h2>
            <button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Collection
            </button>
          </div>

          {/* Create Collection Form */}
          {showCreateForm && (
            <div className="mb-6 p-4 bg-white rounded-lg shadow">
              <form onSubmit={handleCreateCollection} className="flex space-x-4">
                <input
                  type="text"
                  placeholder="Collection name"
                  value={newCollectionName}
                  onChange={(e) => setNewCollectionName(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
              </form>
            </div>
          )}

          {/* Collections Grid */}
          {collections.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No collections</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating a new collection.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {collections.map((collection) => (
                <div key={collection.id} className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-6">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-medium text-gray-900">
                        {collection.title}
                      </h3>
                      <button
                        onClick={() => handleDeleteCollection(collection.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </div>
                    <div className="mt-4 flex items-center text-sm text-gray-500">
                      <BookOpen className="h-4 w-4 mr-1" />
                      {collection.paper_count} papers
                    </div>
                    <div className="mt-2 text-sm text-gray-500">
                      Created {new Date(collection.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="px-6 py-3 bg-gray-50">
                    <Link
                      to={`/collection/${collection.id}`}
                      className="text-indigo-600 hover:text-indigo-900 font-medium"
                    >
                      View Collection →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
