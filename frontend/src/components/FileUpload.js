import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const FileUpload = ({ collectionId, onUpload }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`/ingest/pdf/${collectionId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus({
        type: 'success',
        message: 'PDF uploaded successfully! Processing will begin shortly.',
        taskId: response.data.task_id,
      });

      // Refresh collection data
      onUpload();
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Upload failed',
      });
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Upload PDF</h3>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} disabled={uploading} />
        
        {uploading ? (
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-2"></div>
            <p className="text-sm text-gray-600">Uploading...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <Upload className="h-8 w-8 text-gray-400 mb-2" />
            <p className="text-sm text-gray-600">
              {isDragActive
                ? 'Drop the PDF here...'
                : 'Drag & drop a PDF here, or click to select'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Maximum file size: 50MB
            </p>
          </div>
        )}
      </div>

      {uploadStatus && (
        <div className={`mt-4 p-3 rounded-md flex items-center ${
          uploadStatus.type === 'success'
            ? 'bg-green-50 text-green-800'
            : 'bg-red-50 text-red-800'
        }`}>
          {uploadStatus.type === 'success' ? (
            <CheckCircle className="h-4 w-4 mr-2" />
          ) : (
            <AlertCircle className="h-4 w-4 mr-2" />
          )}
          <span className="text-sm">{uploadStatus.message}</span>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
