import React from 'react';
import { motion } from 'framer-motion';
import { Copy, Download, ThumbsUp, ThumbsDown, Clock } from 'lucide-react';
import type { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([message.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `message-${message.timestamp.getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`max-w-3xl ${isUser ? 'ml-12' : 'mr-12'}`}
      >
        <div
          className={`rounded-lg p-4 shadow-sm ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
          }`}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  isUser ? 'bg-blue-700' : 'bg-gray-600 dark:bg-gray-500'
                }`}
              >
                <span className="text-white text-sm font-medium">
                  {isUser ? 'You' : 'AI'}
                </span>
              </div>
              {!isUser && message.model && (
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">
                  {message.model}
                </span>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 text-xs opacity-70">
                <Clock className="h-3 w-3" />
                <span>{formatTime(message.timestamp)}</span>
              </div>

              {/* Action buttons */}
              <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={handleCopy}
                  className={`p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-600 ${
                    isUser ? 'hover:bg-blue-700' : ''
                  }`}
                  title="Copy message"
                >
                  <Copy className="h-3 w-3" />
                </button>
                <button
                  onClick={handleDownload}
                  className={`p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-600 ${
                    isUser ? 'hover:bg-blue-700' : ''
                  }`}
                  title="Download message"
                >
                  <Download className="h-3 w-3" />
                </button>
                {!isUser && (
                  <>
                    <button
                      className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-600"
                      title="Thumbs up"
                    >
                      <ThumbsUp className="h-3 w-3" />
                    </button>
                    <button
                      className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-600"
                      title="Thumbs down"
                    >
                      <ThumbsDown className="h-3 w-3" />
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
          </div>

          {/* Metadata */}
          {message.metadata && (
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
              <div className="flex items-center justify-between text-xs opacity-70">
                <div className="flex items-center space-x-4">
                  {message.metadata.processing_time && (
                    <span>Processing: {message.metadata.processing_time}s</span>
                  )}
                  {message.metadata.tasks_executed && (
                    <span>{message.metadata.tasks_executed} tasks</span>
                  )}
                  {message.metadata.successful_tasks && (
                    <span>{message.metadata.successful_tasks} successful</span>
                  )}
                </div>
                {copied && (
                  <span className="text-green-600 dark:text-green-400">Copied!</span>
                )}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
