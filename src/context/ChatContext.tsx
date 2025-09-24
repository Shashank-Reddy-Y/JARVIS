import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { ChatState, Conversation, Message, Model } from '../types';

interface ChatContextType extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  createNewConversation: () => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  updateConversationTitle: (id: string, title: string) => void;
  stopGeneration: () => void;
  setSelectedModel: (model: string) => void;
}

type ChatAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_STREAMING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'UPDATE_MESSAGE'; payload: { id: string; content: string } }
  | { type: 'SET_CONVERSATIONS'; payload: Conversation[] }
  | { type: 'ADD_CONVERSATION'; payload: Conversation }
  | { type: 'UPDATE_CONVERSATION'; payload: Conversation }
  | { type: 'DELETE_CONVERSATION'; payload: string }
  | { type: 'SET_CURRENT_CONVERSATION'; payload: Conversation | null }
  | { type: 'SET_MODELS'; payload: Model[] }
  | { type: 'SET_SELECTED_MODEL'; payload: string };

const initialState: ChatState = {
  conversations: [],
  currentConversation: null,
  isLoading: false,
  isStreaming: false,
  error: null,
  selectedModel: 'openai/gpt-oss-20b:free',
  availableModels: [],
};

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_STREAMING':
      return { ...state, isStreaming: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'ADD_MESSAGE':
      const newMessage = action.payload;
      const updatedConversations = state.conversations.map(conv => {
        if (conv.id === state.currentConversation?.id) {
          return {
            ...conv,
            messages: [...conv.messages, newMessage],
            updatedAt: new Date(),
          };
        }
        return conv;
      });
      return {
        ...state,
        conversations: updatedConversations,
        currentConversation: updatedConversations.find(c => c.id === state.currentConversation?.id) || null,
      };
    case 'UPDATE_MESSAGE':
      const updatedMessages = state.currentConversation?.messages.map(msg =>
        msg.id === action.payload.id ? { ...msg, content: action.payload.content } : msg
      ) || [];
      const updatedCurrentConv = state.currentConversation ? {
        ...state.currentConversation,
        messages: updatedMessages,
      } : null;
      return {
        ...state,
        currentConversation: updatedCurrentConv,
        conversations: state.conversations.map(conv =>
          conv.id === state.currentConversation?.id ? updatedCurrentConv! : conv
        ),
      };
    case 'SET_CONVERSATIONS':
      return { ...state, conversations: action.payload };
    case 'ADD_CONVERSATION':
      return {
        ...state,
        conversations: [action.payload, ...state.conversations],
        currentConversation: action.payload,
      };
    case 'UPDATE_CONVERSATION':
      return {
        ...state,
        conversations: state.conversations.map(conv =>
          conv.id === action.payload.id ? action.payload : conv
        ),
        currentConversation: state.currentConversation?.id === action.payload.id ? action.payload : state.currentConversation,
      };
    case 'DELETE_CONVERSATION':
      return {
        ...state,
        conversations: state.conversations.filter(conv => conv.id !== action.payload),
        currentConversation: state.currentConversation?.id === action.payload ? null : state.currentConversation,
      };
    case 'SET_CURRENT_CONVERSATION':
      return { ...state, currentConversation: action.payload };
    case 'SET_MODELS':
      return { ...state, availableModels: action.payload };
    case 'SET_SELECTED_MODEL':
      return { ...state, selectedModel: action.payload };
    default:
      return state;
  }
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Load conversations from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('finance-chat-conversations');
    if (saved) {
      try {
        const conversations = JSON.parse(saved).map((conv: any) => ({
          ...conv,
          createdAt: new Date(conv.createdAt),
          updatedAt: new Date(conv.updatedAt),
          messages: conv.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
          })),
        }));
        dispatch({ type: 'SET_CONVERSATIONS', payload: conversations });
      } catch (error) {
        console.error('Error loading conversations:', error);
      }
    }
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('finance-chat-conversations', JSON.stringify(state.conversations));
  }, [state.conversations]);

  // Load available models
  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/models/openrouter');
      if (response.ok) {
        const models = await response.json();
        dispatch({ type: 'SET_MODELS', payload: models });
      }
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const sendMessage = async (content: string) => {
    if (!content.trim() || state.isStreaming) return;

    dispatch({ type: 'SET_ERROR', payload: null });
    dispatch({ type: 'SET_STREAMING', payload: true });

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    // Add user message to current conversation
    if (state.currentConversation) {
      dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    }

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: content,
          session_id: state.currentConversation?.id,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        model: state.selectedModel,
        metadata: {
          processing_time: data.metadata.processing_time,
          tasks_executed: data.metadata.tasks_executed,
          successful_tasks: data.metadata.successful_tasks,
        },
      };

      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage });

      // Update conversation title if it's the first message
      if (state.currentConversation && state.currentConversation.messages.length === 0) {
        const title = content.length > 50 ? content.substring(0, 50) + '...' : content;
        updateConversationTitle(state.currentConversation.id, title);
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'An error occurred' });
    } finally {
      dispatch({ type: 'SET_STREAMING', payload: false });
    }
  };

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    dispatch({ type: 'ADD_CONVERSATION', payload: newConversation });
  };

  const selectConversation = (id: string) => {
    const conversation = state.conversations.find(conv => conv.id === id);
    if (conversation) {
      dispatch({ type: 'SET_CURRENT_CONVERSATION', payload: conversation });
    }
  };

  const deleteConversation = (id: string) => {
    dispatch({ type: 'DELETE_CONVERSATION', payload: id });
  };

  const updateConversationTitle = (id: string, title: string) => {
    const conversation = state.conversations.find(conv => conv.id === id);
    if (conversation) {
      const updatedConversation = { ...conversation, title, updatedAt: new Date() };
      dispatch({ type: 'UPDATE_CONVERSATION', payload: updatedConversation });
    }
  };

  const stopGeneration = () => {
    dispatch({ type: 'SET_STREAMING', payload: false });
  };

  const setSelectedModel = (model: string) => {
    dispatch({ type: 'SET_SELECTED_MODEL', payload: model });
  };

  const value: ChatContextType = {
    ...state,
    sendMessage,
    createNewConversation,
    selectConversation,
    deleteConversation,
    updateConversationTitle,
    stopGeneration,
    setSelectedModel,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
