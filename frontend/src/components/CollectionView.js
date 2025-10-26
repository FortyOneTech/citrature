import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, BarChart3, MessageCircle, Lightbulb, BookOpen, LogOut, Home } from 'lucide-react';
import FileUpload from './FileUpload';
import TopicSearch from './TopicSearch';
import GraphView from './GraphView';
import ChatInterface from './ChatInterface';
import GapAnalysis from './GapAnalysis';

const CollectionView = ({ user, onLogout }) => {
  const { id } = useParams();
  const [collection, setCollection] = useState(null);
  const [activeTab, setActiveTab] = useState('papers');
  const [loading, setLoading] = useState(true);

  const fetchCollection = useCallback(async () => {
    try {
      const response = await axios.get(`/collections/${id}`);
      setCollection(response.data);
    } catch (error) {
      console.error('Error fetching collection:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchCollection();
  }, [fetchCollection]);

  const tabs = [
    { id: 'papers', name: 'Papers', icon: BookOpen },
    { id: 'graph', name: 'Graph', icon: BarChart3 },
    { id: 'chat', name: 'Chat', icon: MessageCircle },
    { id: 'gaps', name: 'Gaps', icon: Lightbulb },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!collection) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Collection not found</h2>
          <Link to="/" className="text-indigo-600 hover:text-indigo-900">
            Back to Dashboard
          </Link>
        </div>
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
              <Link to="/" className="mr-4">
                <ArrowLeft className="h-6 w-6 text-gray-600 hover:text-gray-900" />
              </Link>
              <BookOpen className="h-8 w-8 text-indigo-600" />
              <div className="ml-2">
                <h1 className="text-2xl font-bold text-gray-900">{collection.title}</h1>
                <p className="text-sm text-gray-500">{collection.paper_count} papers</p>
              </div>
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

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {activeTab === 'papers' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FileUpload collectionId={id} onUpload={fetchCollection} />
                <TopicSearch collectionId={id} onSearch={fetchCollection} />
              </div>
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Papers</h3>
                <div className="text-center py-12">
                  <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No papers yet</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Upload a PDF or search for papers to get started.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'graph' && (
            <GraphView collectionId={id} />
          )}

          {activeTab === 'chat' && (
            <ChatInterface collectionId={id} />
          )}

          {activeTab === 'gaps' && (
            <GapAnalysis collectionId={id} />
          )}
        </div>
      </main>
    </div>
  );
};

export default CollectionView;
