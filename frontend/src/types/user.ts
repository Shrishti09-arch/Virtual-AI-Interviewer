export interface User {
  id: number;
  email: string;
  full_name: string;
  name?: string;
  role_target?: string;
  experience_level?: string;
  bio?: string;
  skills: string[];
  llm_preference: string;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  full_name: string;
}
