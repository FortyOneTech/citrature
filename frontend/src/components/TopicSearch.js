import React, { useState } from 'react';
import { Search, BookOpen } from 'lucide-react';
import axios from 'axios';

const TopicSearch = ({ collectionId, onSearch }) => {
  const [query, setQuery] = useState('');
  const [limit, setLimit] = useState(30);
  const [searching, setSearching] = useState(false);
  const [searchStatus, setSearchStatus] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setSearching(true);
    setSearchStatus(null);

    try {
      const response = await axios.post(`/ingest/topic/${collectionId}`, {
        query: query.trim(),
        limit: limit,
      });

      setSearchStatus({
        type: 'success',
        message: `Search started! Looking for up to ${limit} papers about "${query}".`,
        taskId: response.data.task_id,
      });

      // Clear form
      setQuery('');
      
      // Refresh collection data
      onSearch();
    } catch (error) {
      setSearchStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Search failed',
      });
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Search Topic</h3>
      
      <form onSubmit={handleSearch} className="space-y-4">
        <div>
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-1">
            Search Query
          </label>
          <input
            type="text"
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., machine learning, climate change, quantum computing"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            disabled={searching}
          />
        </div>

        <div>
          <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-1">
            Maximum Papers
          </label>
          <select
            id="limit"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            disabled={searching}
          >
            <option value={10}>10 papers</option>
            <option value={20}>20 papers</option>
            <option value={30}>30 papers</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={searching || !query.trim()}
          className="w-full flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {searching ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Searching...
            </>
          ) : (
            <>
              <Search className="h-4 w-4 mr-2" />
              Search Papers
            </>
          )}
        </button>
      </form>

      {searchStatus && (
        <div className={`mt-4 p-3 rounded-md flex items-center ${
          searchStatus.type === 'success'
            ? 'bg-green-50 text-green-800'
            : 'bg-red-50 text-red-800'
        }`}>
          <BookOpen className="h-4 w-4 mr-2" />
          <span className="text-sm">{searchStatus.message}</span>
        </div>
      )}

      <div className="mt-4 text-xs text-gray-500">
        <p>• Searches Crossref database for relevant papers</p>
        <p>• Free plan limited to 30 papers per search</p>
        <p>• Processing may take a few minutes</p>
      </div>
    </div>
  );
};

export default TopicSearch;
