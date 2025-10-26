import React, { useState, useEffect, useCallback } from 'react';
import { Lightbulb, Play, TrendingUp, Target, BarChart3 } from 'lucide-react';
import axios from 'axios';

const GapAnalysis = ({ collectionId }) => {
  const [insights, setInsights] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState(null);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setAnalysisStatus(null);

    try {
      const response = await axios.post(`/analysis/gaps/${collectionId}`);
      
      setAnalysisStatus({
        type: 'success',
        message: 'Gap analysis started! This may take several minutes.',
        taskId: response.data.task_id,
      });

      // Refresh insights after a delay
      setTimeout(() => {
        fetchInsights();
      }, 10000);
    } catch (error) {
      setAnalysisStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Gap analysis failed',
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const fetchInsights = useCallback(async () => {
    try {
      const response = await axios.get(`/analysis/gaps/${collectionId}`);
      setInsights(response.data);
    } catch (error) {
      console.error('Error fetching insights:', error);
    }
  }, [collectionId]);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  const getScoreColor = (score) => {
    if (score >= 0.7) return 'text-red-600 bg-red-50';
    if (score >= 0.5) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getScoreLabel = (score) => {
    if (score >= 0.7) return 'High Priority';
    if (score >= 0.5) return 'Medium Priority';
    return 'Low Priority';
  };

  return (
    <div className="space-y-6">
      {/* Analysis Controls */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Research Gap Analysis</h3>
        
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-2">
              Analyze your collection to identify research gaps and opportunities.
            </p>
            <p className="text-xs text-gray-500">
              This will examine paper clusters, novelty, and research trajectories.
            </p>
          </div>
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyzing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Run Analysis
              </>
            )}
          </button>
        </div>

        {analysisStatus && (
          <div className={`mt-4 p-3 rounded-md flex items-center ${
            analysisStatus.type === 'success'
              ? 'bg-green-50 text-green-800'
              : 'bg-red-50 text-red-800'
          }`}>
            <Lightbulb className="h-4 w-4 mr-2" />
            <span className="text-sm">{analysisStatus.message}</span>
          </div>
        )}
      </div>

      {/* Insights */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Research Insights</h3>
        
        {insights.length === 0 ? (
          <div className="text-center py-8">
            <Lightbulb className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No insights yet</h3>
            <p className="text-gray-500">
              Run gap analysis to discover research opportunities and gaps in your collection.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {insights.map((insight, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center">
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreColor(insight.score)}`}>
                      {getScoreLabel(insight.score)}
                    </div>
                    <div className="ml-2 text-sm text-gray-500">
                      Score: {(insight.score * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <TrendingUp className="h-4 w-4 mr-1" />
                    {insight.score.toFixed(2)}
                  </div>
                </div>
                
                <p className="text-gray-900 mb-3">{insight.insight}</p>
                
                {insight.evidence && (
                  <div className="bg-gray-50 rounded p-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Evidence</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      {insight.evidence.metric && (
                        <div className="flex items-center">
                          <BarChart3 className="h-4 w-4 mr-2 text-gray-400" />
                          <span className="text-gray-600">
                            {insight.evidence.metric}: {insight.evidence.value?.toFixed(2)}
                          </span>
                        </div>
                      )}
                      {insight.evidence.clusters && (
                        <div className="flex items-center">
                          <Target className="h-4 w-4 mr-2 text-gray-400" />
                          <span className="text-gray-600">
                            {insight.evidence.clusters} clusters
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Analysis Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <Lightbulb className="h-5 w-5 text-blue-400 mr-2 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-blue-900">How Gap Analysis Works</h4>
            <p className="text-sm text-blue-700 mt-1">
              Our AI analyzes your paper collection using clustering, novelty detection, 
              and trajectory analysis to identify research gaps and opportunities.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GapAnalysis;
