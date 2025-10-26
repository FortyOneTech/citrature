import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Bot, User } from 'lucide-react';
import axios from 'axios';

const ChatInterface = ({ collectionId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || sending) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setSending(true);

    try {
      const response = await axios.post(`/chat/${collectionId}`, {
        message: inputMessage.trim(),
        k: 5,
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.answer,
        citations: response.data.citations || [],
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setSending(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="bg-white shadow rounded-lg h-[600px] flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center">
          <MessageCircle className="h-5 w-5 text-indigo-600 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Chat with Collection</h3>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Ask questions about your research papers
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <Bot className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Start a conversation</h3>
            <p className="text-gray-500">
              Ask me anything about your research collection. I can help you understand
              the papers, find connections, and identify research gaps.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="flex items-start">
                  {message.type === 'bot' && (
                    <Bot className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                  )}
                  {message.type === 'user' && (
                    <User className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    {message.citations && message.citations.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {message.citations.map((citation, index) => (
                          <div
                            key={index}
                            className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded"
                          >
                            {citation.title} ({citation.year})
                          </div>
                        ))}
                      </div>
                    )}
                    <p className="text-xs opacity-70 mt-1">
                      {formatTimestamp(message.timestamp)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
        {sending && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
              <div className="flex items-center">
                <Bot className="h-4 w-4 mr-2" />
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex space-x-4">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask about your research papers..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            disabled={sending}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || sending}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
