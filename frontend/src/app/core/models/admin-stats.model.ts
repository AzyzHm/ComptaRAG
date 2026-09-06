import { Role } from './user.model';

export interface LoginEvent {
  id: string;
  uid: string;
  email: string | null;
  display_name: string | null;
  role: Role;
  ip: string | null;
  user_agent: string | null;
  created_at: string | number | null;
}

export interface UsageTotal {
  uid: string;
  email: string | null;
  display_name: string | null;
  role: Role;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  message_count: number;
  updated_at?: string | number | null;
}
