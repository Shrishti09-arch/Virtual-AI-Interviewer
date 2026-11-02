import apiClient from '../api/client';

export const practiceService = {
  getMetadata: async () => {
    const res = await apiClient.get('/practice/metadata');
    return res.data;
  },

  getQuestions: async (params?: Record<string, any>) => {
    const res = await apiClient.get('/practice/questions', { params });
    return res.data;
  },

  executeCode: async (payload: { language: string; code: string; test_cases?: any[] }) => {
    const res = await apiClient.post('/practice/execute-code', payload);
    return res.data;
  },

  startSession: async (payload: {
    job_role: string;
    subject: string;
    programming_language: string;
    difficulty: string;
    total_questions: number;
    interview_type: string;
  }) => {
    const res = await apiClient.post('/practice/session/start', payload);
    return res.data;
  },

  submitSessionAnswer: async (sessionId: number, payload: any) => {
    const res = await apiClient.post(`/practice/session/${sessionId}/answer`, payload);
    return res.data;
  },

  getSessionReport: async (sessionId: number) => {
    const res = await apiClient.get(`/practice/session/${sessionId}/report`);
    return res.data;
  },

  submitQuestionBankAnswer: async (questionId: number, userAnswer: string) => {
    const res = await apiClient.post(`/practice/questions/${questionId}/submit`, {
      question_id: questionId,
      user_answer: userAnswer,
    });
    return res.data;
  },
};
