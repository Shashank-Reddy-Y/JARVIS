import React from 'react';
import { motion } from 'framer-motion';
import { Send, Square, Paperclip } from 'lucide-react';
import { useChat } from '../context/ChatContext';

export function Composer() {
  const { sendMessage, isStreaming, stopGeneration, currentConversation } = useChat();
  const [message, setMessage] = React.useState('');
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isStreaming) {
      await sendMessage(message.trim());
      setMessage('');
      adjustTextareaHeight();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  React.useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  const handleStop = () => {
    stopGeneration();
  };

  if (!currentConversation) {
    return (
      <div className="p-4 text-center text-gray-500 dark:text-gray-400">
        <p>Select a conversation to start chatting</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-end space-x-3">
          {/* Attachment button */}
          <button
            type="button"
            className="flex-shrink-0 p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            title="Attach file"
          >
            <Paperclip className="h-5 w-5" />
          </button>

          {/* Textarea */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about investments, savings, loans, or any financial topic..."
              className="w-full resize-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[44px] max-h-32 overflow-y-auto"
              rows={1}
              disabled={isStreaming}
            />

            {/* Character count */}
            {message.length > 0 && (
              <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                {message.length}
              </div>
            )}
          </div>

          {/* Send/Stop button */}
          <button
            type={isStreaming ? 'button' : 'submit'}
            onClick={isStreaming ? handleStop : undefined}
            disabled={!message.trim() && !isStreaming}
            className={`flex-shrink-0 p-2 rounded-lg transition-colors ${
              isStreaming
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : message.trim()
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-200 dark:bg-gray-600 text-gray-400 cursor-not-allowed'
            }`}
            title={isStreaming ? 'Stop generation' : 'Send message'}
          >
            {isStreaming ? (
              <Square className="h-5 w-5" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </div>

        {/* Helper text */}
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Press Enter to send, Shift+Enter for new line
        </div>
      </form>
    </div>
  );
}
