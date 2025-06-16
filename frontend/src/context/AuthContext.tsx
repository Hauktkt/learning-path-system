"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User, LoginData, RegisterData, AuthResponse } from "@/types";
// import axios from "axios"; // Không cần axios trực tiếp ở đây nữa
// import { API_BASE_URL } from "@/config"; // Không cần trực tiếp URL ở đây nữa
import { login as apiLogin, register as apiRegister, logout as apiLogout, getCurrentUser as apiGetCurrentUser } from "@/api/authService";

interface AuthContextType {
  user: User | null;
  login: (data: LoginData) => Promise<boolean>;
  register: (data: RegisterData) => Promise<boolean>;
  logout: () => Promise<void>; // Sửa thành Promise<void>
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem("token");
      if (storedToken) {
        try {
          // Nếu có token, thử lấy thông tin user từ API
          const currentUser = await apiGetCurrentUser();
          setUser(currentUser);
          // Cập nhật lại user data trong localStorage nếu cần
          localStorage.setItem("user", JSON.stringify(currentUser));
        } catch (error) {
          console.error("Failed to fetch current user with token:", error);
          // Token không hợp lệ hoặc hết hạn, xóa nó đi
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          localStorage.removeItem("username");
          setUser(null);
        }
      } else {
        // Kiểm tra user cũ phòng trường hợp token bị xóa nhưng user chưa bị xóa
        const storedUser = localStorage.getItem("user");
        if (storedUser) {
          localStorage.removeItem("user");
          localStorage.removeItem("username");
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (data: LoginData): Promise<boolean> => {
    setIsLoading(true);
    try {
      const response = await apiLogin(data);
      if (response.token && response.user) {
        localStorage.setItem("token", response.token);
        localStorage.setItem("user", JSON.stringify(response.user));
        localStorage.setItem("username", response.user.username);
        setUser(response.user);
        setIsLoading(false);
        return true;
      } else {
        // Xử lý trường hợp API trả về không như mong đợi
        console.error("Login response missing token or user data");
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error("Login failed:", error);
      // Xóa token cũ nếu có lỗi đăng nhập
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem("username");
      setUser(null);
      setIsLoading(false);
      return false;
    }
  };

  const register = async (data: RegisterData): Promise<boolean> => {
    setIsLoading(true);
    try {
      const response = await apiRegister(data);
      if (response.token && response.user) {
        localStorage.setItem("token", response.token);
        localStorage.setItem("user", JSON.stringify(response.user));
        localStorage.setItem("username", response.user.username);
        setUser(response.user);
        setIsLoading(false);
        return true;
      } else {
        console.error("Register response missing token or user data");
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error("Registration failed:", error);
      setIsLoading(false);
      return false;
    }
  };

  const logout = async (): Promise<void> => {
    setIsLoading(true);
    const token = localStorage.getItem("token");

    // Save the learning path ID before logout to preserve it
    const savedPathId = localStorage.getItem("savedLearningPathId");

    try {
      if (token) {
        await apiLogout(); // Gọi API backend để logout
      }
    } catch (error) {
      // Vẫn tiếp tục logout ở frontend ngay cả khi API backend lỗi
      console.error("API logout failed, proceeding with client-side logout:", error);
    } finally {
      // Remove auth-related items but preserve learning path data
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem("username");

      // Restore the saved path ID if it existed
      if (savedPathId) {
        localStorage.setItem("savedLearningPathId", savedPathId);
      }

      setUser(null);
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
} 