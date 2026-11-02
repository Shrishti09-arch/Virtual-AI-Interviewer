import apiClient from '../api/client';

export const authService = {
  login: async (email: string, password: string) => {
    const res = await apiClient.post('/auth/login', { email, password });
    return res.data;
  },

  register: async (payload: { email: string; password: string; full_name: string; role_target?: string; experience_level?: string }) => {
    const res = await apiClient.post('/auth/register', payload);
    return res.data;
  },

  logout: async () => {
    const res = await apiClient.post('/auth/logout');
    return res.data;
  },

  getCurrentUser: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },

  updateProfile: async (payload: { full_name?: string; role_target?: string; experience_level?: string; bio?: string; skills?: string[] }) => {
    const res = await apiClient.put('/auth/profile', payload);
    return res.data;
  },

  updateAIPreferences: async (payload: { llm_preference: string; groq_api_key?: string; ollama_endpoint?: string }) => {
    const res = await apiClient.put('/auth/ai-preferences', payload);
    return res.data;
  },
};
