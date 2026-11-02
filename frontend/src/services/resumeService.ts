import apiClient from '../api/client';

export const resumeService = {
  analyzeUpload: async (formData: FormData) => {
    const res = await apiClient.post('/resumes/analyze-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  analyzeText: async (targetRole: string, resumeText: string, jobDescription?: string) => {
    const formData = new FormData();
    formData.append('target_role', targetRole);
    formData.append('resume_text', resumeText);
    if (jobDescription) formData.append('job_description', jobDescription);

    const res = await apiClient.post('/resumes/analyze-text', formData);
    return res.data;
  },

  getExtractedData: async (resumeId: number) => {
    const res = await apiClient.get(`/resumes/${resumeId}/extracted`);
    return res.data;
  },

  updateExtractedData: async (resumeId: number, extractedData: any) => {
    const res = await apiClient.put(`/resumes/${resumeId}/extracted`, { extracted_data: extractedData });
    return res.data;
  },

  applyCorrectionAction: async (analysisId: number, correctionId: string, action: 'accept' | 'reject') => {
    const res = await apiClient.post(`/resumes/${analysisId}/corrections/${correctionId}`, { action });
    return res.data;
  },

  optimizeForRole: async (payload: any) => {
    const res = await apiClient.post('/resumes/optimize-role', payload);
    return res.data;
  },

  matchJobDescription: async (payload: { resume_text?: string; resume_id?: number; job_description: string; target_role?: string }) => {
    const res = await apiClient.post('/resumes/match-job-description', payload);
    return res.data;
  },

  generatePdf: async (resumeData: any) => {
    const res = await apiClient.post('/resumes/generate-pdf', resumeData, { responseType: 'blob' });
    return res.data;
  },

  generateDocx: async (resumeData: any) => {
    const res = await apiClient.post('/resumes/generate-docx', resumeData, { responseType: 'blob' });
    return res.data;
  },

  deleteResume: async (resumeId: number) => {
    const res = await apiClient.delete(`/resumes/${resumeId}`);
    return res.data;
  },
};
