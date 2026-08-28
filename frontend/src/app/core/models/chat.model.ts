export interface ChatRequest {
  query: string;
}

export interface ChatResponse {
  response: string;
  category?: string | null;
}

export type ChatRole = 'user' | 'assistant';

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  category?: string | null;
  createdAt: number;
}
