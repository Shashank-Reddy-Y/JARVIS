export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  model?: string;
  metadata?: {
    processing_time?: number;
    tasks_executed?: number;
    successful_tasks?: number;
  };
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  selectedModel: string;
  availableModels: Model[];
}

export interface Model {
  id: string;
  name: string;
  cost: number;
  supports_streaming: boolean;
}

export interface ApiResponse {
  session_id: string;
  response: string;
  metadata: {
    timestamp: string;
    processing_time: number;
    status: string;
    tasks_executed: number;
    successful_tasks: number;
  };
  query: string;
  detailed_results?: {
    tasks: any[];
    results: any;
  };
}
