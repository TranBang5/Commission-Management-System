import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const token = localStorage.getItem('token');
        if (token) {
          const response = await axios.post(
            `${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/auth/refresh`,
            { token }
          );
          
          const { token: newToken } = response.data.data;
          localStorage.setItem('token', newToken);
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  refreshToken: (data) => api.post('/auth/refresh', data),
  updateProfile: (profileData) => api.put('/auth/profile', profileData),
  changePassword: (passwordData) => api.put('/auth/change-password', passwordData),
};

// Commission API
export const commissionAPI = {
  getAll: (params) => api.get('/commissions', { params }),
  getById: (id) => api.get(`/commissions/${id}`),
  create: (data) => api.post('/commissions', data),
  update: (id, data) => api.put(`/commissions/${id}`, data),
  delete: (id) => api.delete(`/commissions/${id}`),
  approve: (id, data) => api.post(`/commissions/${id}/approve`, data),
  dispute: (id, data) => api.post(`/commissions/${id}/dispute`, data),
  calculate: (data) => api.post('/commissions/calculate', data),
  export: (params) => api.get('/commissions/export', { params, responseType: 'blob' }),
  getByPeriod: (year, month) => api.get(`/commissions/period/${year}/${month}`),
  getByEmployee: (employeeId) => api.get(`/commissions/employee/${employeeId}`),
  getByProject: (projectId) => api.get(`/commissions/project/${projectId}`),
  getPendingApproval: () => api.get('/commissions/pending-approval'),
  getDisputes: () => api.get('/commissions/disputes'),
};

// Project API
export const projectAPI = {
  getAll: (params) => api.get('/projects', { params }),
  getById: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
  getActive: () => api.get('/projects/active'),
  getOverdue: () => api.get('/projects/overdue'),
  getByManager: (managerId) => api.get(`/projects/manager/${managerId}`),
  getByTeamMember: (memberId) => api.get(`/projects/team-member/${memberId}`),
  updateProgress: (id, progress) => api.put(`/projects/${id}/progress`, { progress }),
  addTeamMember: (id, memberData) => api.post(`/projects/${id}/team`, memberData),
  removeTeamMember: (id, memberId) => api.delete(`/projects/${id}/team/${memberId}`),
  uploadDocument: (id, formData) => api.post(`/projects/${id}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

// User API
export const userAPI = {
  getAll: (params) => api.get('/users', { params }),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  getActive: () => api.get('/users/active'),
  getByRole: (role) => api.get(`/users/role/${role}`),
  updatePermissions: (id, permissions) => api.put(`/users/${id}/permissions`, { permissions }),
  activate: (id) => api.post(`/users/${id}/activate`),
  deactivate: (id) => api.post(`/users/${id}/deactivate`),
  resetPassword: (id) => api.post(`/users/${id}/reset-password`),
  uploadAvatar: (id, formData) => api.post(`/users/${id}/avatar`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

// AI API
export const aiAPI = {
  calculateReward: (data) => api.post('/ai/calculate-reward', data),
  processFeedback: (data) => api.post('/ai/process-feedback', data),
  detectAnomalies: (data) => api.post('/ai/detect-anomalies', data),
  suggestKPIs: (data) => api.post('/ai/suggest-kpis', data),
  forecastCommission: (data) => api.post('/ai/forecast-commission', data),
  analyzeTopPerformers: (data) => api.post('/ai/analyze-top-performers', data),
  analyzeDispute: (data) => api.post('/ai/analyze-dispute', data),
  batchProcess: (data) => api.post('/ai/batch-process', data),
  trainModels: (data) => api.post('/ai/train-models', data),
  getHealth: () => api.get('/ai/health'),
};

// Report API
export const reportAPI = {
  getDashboard: () => api.get('/reports/dashboard'),
  getCommissionReport: (params) => api.get('/reports/commission', { params }),
  getProjectReport: (params) => api.get('/reports/project', { params }),
  getUserReport: (params) => api.get('/reports/user', { params }),
  getPerformanceReport: (params) => api.get('/reports/performance', { params }),
  getFinancialReport: (params) => api.get('/reports/financial', { params }),
  exportReport: (type, params) => api.get(`/reports/${type}/export`, { 
    params, 
    responseType: 'blob' 
  }),
};

// Settings API
export const settingsAPI = {
  get: () => api.get('/settings'),
  update: (data) => api.put('/settings', data),
  getCommissionRules: () => api.get('/settings/commission-rules'),
  updateCommissionRules: (data) => api.put('/settings/commission-rules', data),
  getKPITemplates: () => api.get('/settings/kpi-templates'),
  updateKPITemplates: (data) => api.put('/settings/kpi-templates', data),
  getNotificationSettings: () => api.get('/settings/notifications'),
  updateNotificationSettings: (data) => api.put('/settings/notifications', data),
};

// File Upload API
export const uploadAPI = {
  uploadFile: (formData) => api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  deleteFile: (filename) => api.delete(`/upload/${filename}`),
};

// Health Check API
export const healthAPI = {
  check: () => api.get('/health'),
  getSystemStatus: () => api.get('/health/system'),
  getDatabaseStatus: () => api.get('/health/database'),
  getRedisStatus: () => api.get('/health/redis'),
};

// Analytics API
export const analyticsAPI = {
  getOverview: () => api.get('/analytics/overview'),
  getTrends: (params) => api.get('/analytics/trends', { params }),
  getPerformanceMetrics: (params) => api.get('/analytics/performance', { params }),
  getTopPerformers: (params) => api.get('/analytics/top-performers', { params }),
  getProjectAnalytics: (projectId) => api.get(`/analytics/project/${projectId}`),
  getUserAnalytics: (userId) => api.get(`/analytics/user/${userId}`),
};

export default api; 