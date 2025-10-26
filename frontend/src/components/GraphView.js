import React, { useState, useEffect, useCallback } from 'react';
import { BarChart3, Play, Download } from 'lucide-react';
import axios from 'axios';

const GraphView = ({ collectionId }) => {
  const [graphData, setGraphData] = useState(null);
  const [building, setBuilding] = useState(false);
  const [buildStatus, setBuildStatus] = useState(null);
  const [mode, setMode] = useState('bfs');
  const [depth, setDepth] = useState(3);

  const fetchGraphData = useCallback(async () => {
    try {
      const response = await axios.get(`/graph/${collectionId}`);
      setGraphData(response.data);
    } catch (error) {
      console.error('Error fetching graph data:', error);
    }
  }, [collectionId]);

  useEffect(() => {
    fetchGraphData();
  }, [fetchGraphData]);

  const handleBuildGraph = async () => {
    setBuilding(true);
    setBuildStatus(null);

    try {
      const response = await axios.post(`/graph/build/${collectionId}`, {
        mode,
        depth,
      });

      setBuildStatus({
        type: 'success',
        message: 'Graph building started! This may take several minutes.',
        taskId: response.data.task_id,
      });

      // Refresh graph data after a delay
      setTimeout(() => {
        fetchGraphData();
      }, 5000);
    } catch (error) {
      setBuildStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Graph building failed',
      });
    } finally {
      setBuilding(false);
    }
  };

  const handleExportGraph = () => {
    if (!graphData) return;

    const exportData = {
      nodes: graphData.nodes,
      edges: graphData.edges,
      metadata: {
        total_papers: graphData.total_papers,
        total_citations: graphData.total_citations,
        exported_at: new Date().toISOString(),
      },
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `graph-${collectionId}-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Graph Controls */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Citation Graph</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Traversal Mode
            </label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="bfs">Breadth-First Search</option>
              <option value="dfs">Depth-First Search</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Depth Limit
            </label>
            <select
              value={depth}
              onChange={(e) => setDepth(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value={1}>1 level</option>
              <option value={2}>2 levels</option>
              <option value={3}>3 levels</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={handleBuildGraph}
              disabled={building}
              className="w-full flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {building ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Building...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Build Graph
                </>
              )}
            </button>
          </div>
        </div>

        {buildStatus && (
          <div className={`p-3 rounded-md flex items-center ${
            buildStatus.type === 'success'
              ? 'bg-green-50 text-green-800'
              : 'bg-red-50 text-red-800'
          }`}>
            <BarChart3 className="h-4 w-4 mr-2" />
            <span className="text-sm">{buildStatus.message}</span>
          </div>
        )}
      </div>

      {/* Graph Visualization */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Graph Visualization</h3>
          {graphData && graphData.nodes.length > 0 && (
            <button
              onClick={handleExportGraph}
              className="flex items-center px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              <Download className="h-4 w-4 mr-1" />
              Export
            </button>
          )}
        </div>

        {graphData && graphData.nodes.length > 0 ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-gray-50 p-3 rounded">
                <div className="font-medium text-gray-900">Papers</div>
                <div className="text-2xl font-bold text-indigo-600">{graphData.total_papers}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="font-medium text-gray-900">Citations</div>
                <div className="text-2xl font-bold text-indigo-600">{graphData.total_citations}</div>
              </div>
            </div>
            
            <div className="h-96 border border-gray-200 rounded-lg flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Graph visualization would appear here</p>
                <p className="text-sm text-gray-400 mt-1">
                  In a full implementation, this would show an interactive force-directed graph
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No graph data</h3>
            <p className="mt-1 text-sm text-gray-500">
              Build a citation graph to visualize paper relationships.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphView;
