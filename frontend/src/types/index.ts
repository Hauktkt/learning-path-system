export interface Course {
  duration: number;
  level: string;
  title: string;
  topics: string[];
}

export interface DailyTask {
  date: string;
  day_of_week: string;
  tasks: string[];
}

export interface Phase {
  duration: number;
  name: string;
  tasks: string[];
}

export interface LearningPath {
  courses: Course[];
  daily_hours: number;
  daily_plan: DailyTask[];
  duration: number;
  field: string;
  interests: string[];
  is_fallback: boolean;
  level: string;
  overview: string;
  phases: Phase[];
  projects: string[];
  resources: string[];
  tips: string[];
}

export interface LearningPathResponse {
  learning_path: LearningPath;
}

export interface FormData {
  field: string;
  level: string;
  duration: number;
  daily_hours: number;
  interests: string[];
}

export interface TaskStatus {
  date: string;
  completed: boolean;
}

export interface User {
  id: string;
  username: string;
  email: string;
  name?: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  name?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface ProfileData {
  name?: string;
  email?: string;
  currentPassword?: string;
  newPassword?: string;
}

export interface LearningPathParams {
  field: string;
  level: string;
  duration: number;
  daily_hours: number;
  interests: string[];
}

export interface LearningPathData {
  courses: Course[];
  daily_hours: number;
  daily_plan: DailyTask[];
  duration: number;
  field: string;
  interests: string[];
  is_fallback: boolean;
  level: string;
  overview: string;
  phases: Phase[];
  projects: string[];
  resources: string[];
  tips: string[];
}

export interface LearningPathResponse {
  learning_path: LearningPathData;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  date: string | null;
}

export interface ProgressItem {
  id: number;
  skill_name: string;
  progress_percentage: number;
  last_updated: string | null;
}

export interface StoredLearningPath {
  id: number;
  field: string;
  level: string;
  duration: number;
  daily_hours: number;
  total_hours: number;
  created_at: string;
  tasks_by_phase?: { [phase: string]: Task[] };
  progress?: ProgressItem[];
}

export interface StoredLearningPathList {
  id: number;
  field: string;
  level: string;
  duration: number;
  daily_hours: number;
  total_hours: number;
  created_at: string;
  progress: {
    total_tasks: number;
    completed_tasks: number;
    completion_percentage: number;
    skills: ProgressItem[];
  };
}

export interface DailyStat {
  date: string;
  day_of_week: string;
  completed_tasks: number;
}

export interface WeeklyStats {
  daily_stats: DailyStat[];
  overall_stats: {
    total_paths: number;
    total_tasks: number;
    completed_tasks: number;
    completion_percentage: number;
    current_streak: number;
  };
  labels?: string[];
  data?: number[];
}

export interface TaskToggleResponse {
  task: {
    id: number;
    completed: boolean;
  };
  progress: {
    skill_name: string;
    progress_percentage: number;
  };
}

export interface TaskNotesResponse {
  task: {
    id: number;
    description: string;
  };
}

export interface SavePathResponse {
  message: string;
  path_id: number;
} 