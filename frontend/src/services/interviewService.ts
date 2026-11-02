import apiClient from '../api/client';

export const interviewService = {
  startSession: async (payload: {
    role_title: string;
    interview_type: string;
    experience_level: string;
    difficulty: string;
    technical_subjects: string[];
    interview_duration_mins: number;
    target_company?: string;
    total_questions: number;
    recording_consent?: boolean;
  }) => {
    const res = await apiClient.post('/interviews/start', payload);
    return res.data;
  },

  getSession: async (sessionId: number) => {
    const res = await apiClient.get(`/interviews/${sessionId}`);
    return res.data;
  },

  submitAnswer: async (sessionId: number, payload: {
    question_id: number;
    candidate_answer: string;
    time_spent_seconds: number;
    pauses_count: number;
    has_local_recording?: boolean;
    recording_storage_key?: string;
  }) => {
    const res = await apiClient.post(`/interviews/${sessionId}/answer`, payload);
    return res.data;
  },

  completeInterview: async (sessionId: number) => {
    const res = await apiClient.post(`/interviews/${sessionId}/complete`);
    return res.data;
  },

  uploadRecording: async (sessionId: number, blob: Blob, filename = 'recording.webm') => {
    const formData = new FormData();
    formData.append('file', blob, filename);
    const res = await apiClient.post(`/interviews/${sessionId}/recording`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  downloadPdfScorecard: async (sessionId: number) => {
    const res = await apiClient.get(`/interviews/${sessionId}/report-pdf`, { responseType: 'blob' });
    return res.data;
  },

  deleteRecording: async (sessionId: number) => {
    const res = await apiClient.delete(`/interviews/${sessionId}/recording`);
    return res.data;
  },

  deleteSession: async (sessionId: number) => {
    const res = await apiClient.delete(`/interviews/${sessionId}`);
    return res.data;
  },
};
