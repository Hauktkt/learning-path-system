// This file is now deprecated and replaced by import modules in src/api/ folder
// Please use the appropriate service from src/api/ instead
// For example:
// - import { generateLearningPath } from '@/api/learningPathService';
// - import { login, register } from '@/api/authService';

// import { LearningPathResponse, LoginData, RegisterData, AuthResponse, ProfileData } from "@/types";
import axios from 'axios';

// Base API URL - can be overridden by environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

// Axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptor to add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Authentication APIs
export const authAPI = {
  register: async (userData: { username: string; email: string; password: string }) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  login: async (credentials: { username: string; password: string }) => {
    const response = await apiClient.post('/auth/login', credentials);
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
    }
    return response.data;
  },

  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    localStorage.removeItem('token');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data.user;
  },

  checkUsername: async (username: string) => {
    const response = await apiClient.get(`/auth/users/${username}/exists`);
    return response.data.exists;
  }
};

// Learning Path APIs
export const learningPathAPI = {
  createLearningPath: async (data: {
    field: string;
    level: string;
    duration: number;
    daily_hours: number;
    interests: string[];
  }) => {
    const response = await apiClient.post('/learning-path', data);
    return response.data;
  },

  getAllPaths: async () => {
    const response = await apiClient.get('/progress/learning-paths');
    return response.data.learning_paths;
  },

  getPathById: async (pathId: number) => {
    const response = await apiClient.get(`/progress/learning-paths/${pathId}`);
    return response.data.learning_path;
  },

  savePath: async (pathId: number, learningPathData: unknown) => {
    const response = await apiClient.post(`/progress/learning-paths/${pathId}/save`, learningPathData);
    return response.data;
  },

  toggleTask: async (taskId: number) => {
    const response = await apiClient.post(`/progress/tasks/${taskId}/toggle`);
    return response.data;
  },

  addTaskNotes: async (taskId: number, notes: string) => {
    const response = await apiClient.post(`/progress/tasks/${taskId}/notes`, { notes });
    return response.data;
  },

  getWeeklyStats: async () => {
    const response = await apiClient.get('/progress/stats/weekly');
    return response.data;
  }
};

export default {
  auth: authAPI,
  learningPath: learningPathAPI
}; 