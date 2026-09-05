export type ChatRole = 'user' | 'assistant';

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  category?: string | null;
  token_usage?: TokenUsage | null;
  created_at?: string | number | null;
}

export interface ChatSummary {
  id: string;
  owner_uid: string;
  title: string;
  created_at?: string | number | null;
  updated_at?: string | number | null;
}

export interface ChatDetail extends ChatSummary {
  messages: ChatMessage[];
}

export interface SendMessageResponse {
  response: string;
  category?: string | null;
  chat_id: string;
}
