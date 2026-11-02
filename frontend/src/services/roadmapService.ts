import apiClient from '../api/client';

export const roadmapService = {
  getUserRoadmaps: async () => {
    const res = await apiClient.get('/roadmaps');
    return res.data;
  },

  generateRoadmap: async (payload: {
    target_role: string;
    current_level: string;
    education: string;
    existing_skills: string[];
    daily_study_hours: number;
    career_goal: string;
    timeline_months?: number;
  }) => {
    const res = await apiClient.post('/roadmaps/generate', payload);
    return res.data;
  },

  toggleTask: async (roadmapId: number, milestoneId: number, taskId: string, isDone: boolean) => {
    const res = await apiClient.put(`/roadmaps/${roadmapId}/milestones/${milestoneId}/task`, {
      task_id: taskId,
      is_done: isDone,
    });
    return res.data;
  },

  deleteRoadmap: async (roadmapId: number) => {
    const res = await apiClient.delete(`/roadmaps/${roadmapId}`);
    return res.data;
  },
};
