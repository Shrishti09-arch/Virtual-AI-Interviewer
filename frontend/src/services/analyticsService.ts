import apiClient from '../api/client';

export const analyticsService = {
  getDashboardAnalytics: async () => {
    const res = await apiClient.get('/analytics/dashboard');
    return res.data;
  },

  getProgressAnalytics: async () => {
    const res = await apiClient.get('/analytics/progress');
    return res.data;
  },
};
