import axios from "axios";
import { API_BASE_URL } from "../config";
import { AuthResponse, User } from "../types";

// Debug mode
const DEBUG = true;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (DEBUG) {
    console.log(`🚀 Auth Request: ${config.method?.toUpperCase()} ${config.url}`, config);
  }

  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    if (DEBUG) {
      console.log(`✅ Auth Response: ${response.status}`, response.data);
    }
    return response;
  },
  (error) => {
    if (DEBUG) {
      console.error(`❌ Auth Error: ${error.message}`, error.response?.data);
    }

    // Nếu lỗi 401 và không phải là request đăng nhập/đăng ký
    if (error.response &&
      error.response.status === 401 &&
      !error.config.url.includes('/login') &&
      !error.config.url.includes('/register')) {
      // Xóa token và thông tin người dùng
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('username');

      // Điều hướng tới trang đăng nhập
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

export const register = async (userData: { username: string; email: string; password: string }): Promise<AuthResponse> => {
  try {
    const response = await api.post("/api/auth/register", userData);
    if (response.data.token) {
      localStorage.setItem("token", response.data.token);
      localStorage.setItem("username", response.data.user.username);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }
    return response.data;
  } catch (error) {
    console.error("Registration error:", error);
    throw error;
  }
};

export const login = async (credentials: { username: string; password: string }): Promise<AuthResponse> => {
  try {
    const response = await api.post("/api/auth/login", credentials);
    if (response.data.token) {
      localStorage.setItem("token", response.data.token);
      localStorage.setItem("username", response.data.user.username);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }
    return response.data;
  } catch (error) {
    console.error("Login error:", error);
    throw error;
  }
};

export const logout = async (): Promise<{ message: string }> => {
  try {
    // Lưu lại savedLearningPathId trước khi đăng xuất
    const savedPathId = localStorage.getItem("savedLearningPathId");

    const response = await api.post("/api/auth/logout");

    // Xóa thông tin xác thực
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("user");

    // Khôi phục ID lộ trình đã lưu
    if (savedPathId) {
      localStorage.setItem("savedLearningPathId", savedPathId);
    }

    return response.data;
  } catch (error) {
    console.error("Logout error:", error);

    // Xóa thông tin xác thực ngay cả khi API báo lỗi
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("user");

    // Giả lập response khi API lỗi
    return { message: "Đã đăng xuất khỏi phiên" };
  }
};

export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await api.get("/api/auth/me");
    return response.data.user;
  } catch (error) {
    console.error("Get current user error:", error);
    throw error;
  }
};

export const checkUsernameExists = async (username: string): Promise<boolean> => {
  try {
    const response = await api.get(`/api/auth/users/${username}/exists`);
    return response.data.exists;
  } catch (error) {
    console.error("Check username exists error:", error);
    return false; // Giả sử username không tồn tại nếu có lỗi
  }
}; 