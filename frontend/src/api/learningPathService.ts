import axios from "axios";
import { LearningPathParams, LearningPathResponse, SavePathResponse, StoredLearningPath, StoredLearningPathList, TaskNotesResponse, TaskToggleResponse, WeeklyStats } from "../types";
import { API_BASE_URL } from "../config";

// Add debug flag
const DEBUG = true;

// Tạo axios instance với baseURL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Biến để theo dõi nếu chúng ta đang làm mới token
let isRefreshing = false;
// Hàng đợi các yêu cầu cần thử lại sau khi làm mới token
let failedQueue: { resolve: (value: string | null) => void; reject: (reason?: any) => void }[] = [];

// Xử lý thành công hàng đợi
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (DEBUG) {
    console.log(`🚀 Request: ${config.method?.toUpperCase()} ${config.url}`, config);
  }

  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for debugging and handling token expiration
api.interceptors.response.use(
  (response) => {
    if (DEBUG) {
      console.log(`✅ Response: ${response.status}`, response.data);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (DEBUG) {
      console.error(`❌ Error: ${error.message}`, error.response?.data);
    }

    // Xử lý lỗi 401 (Unauthorized)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Nếu đang làm mới token, đưa yêu cầu vào hàng đợi
        return new Promise<string | null>(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            if (token) {
              originalRequest.headers['Authorization'] = 'Bearer ' + token;
              return api(originalRequest);
            }
            return Promise.reject(new Error('Token không hợp lệ'));
          })
          .catch(err => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      // Thử đăng nhập lại nếu có thông tin user
      try {
        const userJson = localStorage.getItem('user');
        if (!userJson) {
          // Nếu không có user, điều hướng về trang login
          window.location.href = '/login';
          return Promise.reject(error);
        }

        const user = JSON.parse(userJson);

        // Thông báo cho người dùng
        console.log('Phiên đăng nhập hết hạn, đang tự động làm mới...');

        // Xóa token cũ
        localStorage.removeItem('token');

        // Điều hướng về trang login để người dùng đăng nhập lại
        window.location.href = '/login';
        processQueue(error, null);
        return Promise.reject(error);
      } catch (refreshError) {
        processQueue(refreshError, null);
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Tạo lộ trình học tập
 */
export const generateLearningPath = async (params: LearningPathParams): Promise<LearningPathResponse> => {
  // Thêm username vào query string
  const username = localStorage.getItem("username") || "test_user";

  // Kiểm tra params có đầy đủ không
  if (!params.field || !params.level || !params.duration) {
    throw new Error("Thiếu thông tin cần thiết: field, level, duration");
  }

  // Đảm bảo daily_hours có giá trị
  const finalParams = {
    field: params.field,
    level: params.level,
    duration: params.duration,
    daily_hours: params.daily_hours || 2,
    interests: params.interests || []
  };

  console.log('Final params before API call:', finalParams);

  try {
    // Gọi API với endpoint chính xác
    const response = await api.post('/api/learning-path', finalParams, {
      params: { username }
    });

    if (!response.data || !response.data.learning_path) {
      throw new Error("Invalid response format from API");
    }

    return response.data;
  } catch (error) {
    console.error('Error in generateLearningPath:', error);
    throw error;
  }
};

/**
 * Lưu lộ trình học tập vào cơ sở dữ liệu (tạo mới nếu pathId = 0)
 */
export const createOrUpdateLearningPath = async (pathId: number, pathResponse: LearningPathResponse): Promise<SavePathResponse> => {
  // API mong đợi một object chứa key 'learning_path'
  const requestBody = { learning_path: pathResponse.learning_path };
  try {
    console.log(`Calling save API for pathId: ${pathId} with data:`, requestBody);
    const response = await api.post(`/api/progress/learning-paths/${pathId}/save`, requestBody);
    return response.data;
  } catch (error) {
    console.error(`Error in createOrUpdateLearningPath for pathId ${pathId}:`, error);
    throw error;
  }
};

/**
 * Lấy danh sách lộ trình học tập của người dùng
 */
export const getUserLearningPaths = async (): Promise<StoredLearningPathList[]> => {
  try {
    const response = await api.get("/api/progress/learning-paths");
    return response.data.learning_paths || [];
  } catch (error) {
    console.error('Error in getUserLearningPaths:', error);
    // Trả về mảng rỗng trong trường hợp lỗi để tránh lỗi null/undefined
    return [];
  }
};

/**
 * Lấy chi tiết lộ trình học tập theo ID
 */
export const getLearningPathById = async (id: number): Promise<StoredLearningPath> => {
  try {
    const response = await api.get(`/api/progress/learning-paths/${id}`);
    return response.data.learning_path;
  } catch (error) {
    console.error('Error in getLearningPathById:', error);
    throw error;
  }
};

/**
 * Đánh dấu nhiệm vụ đã hoàn thành/chưa hoàn thành
 */
export const toggleTaskCompletion = async (taskId: number): Promise<TaskToggleResponse> => {
  try {
    const response = await api.post(`/api/progress/tasks/${taskId}/toggle`);
    return response.data;
  } catch (error) {
    console.error('Error in toggleTaskCompletion:', error);
    throw error;
  }
};

/**
 * Cập nhật ghi chú cho nhiệm vụ
 */
export const updateTaskNotes = async (taskId: number, notes: string): Promise<TaskNotesResponse> => {
  try {
    const response = await api.post(`/api/progress/tasks/${taskId}/notes`, { notes });
    return response.data;
  } catch (error) {
    console.error('Error in updateTaskNotes:', error);
    throw error;
  }
};

/**
 * Lấy thống kê học tập theo tuần
 */
export const getWeeklyStats = async (): Promise<WeeklyStats> => {
  try {
    const response = await api.get("/api/progress/stats/weekly");
    return response.data;
  } catch (error) {
    console.error('Error in getWeeklyStats:', error);
    return {
      data: [0, 0, 0, 0, 0, 0, 0],
      labels: ["CN", "T2", "T3", "T4", "T5", "T6", "T7"],
      daily_stats: [],
      overall_stats: {
        current_streak: 0,
        total_paths: 0,
        total_tasks: 0,
        completed_tasks: 0,
        completion_percentage: 0
      }
    };
  }
};

export const deleteLearningPath = async (pathId: number): Promise<{ message: string }> => {
  try {
    const response = await api.delete(`/api/learning-paths/${pathId}`);
    return response.data;
  } catch (error) {
    console.error('Error in deleteLearningPath:', error);
    throw error;
  }
}; 