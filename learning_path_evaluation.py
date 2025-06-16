from typing import List, Dict, Any
import numpy as np
from evaluation import SystemEvaluator
from datetime import datetime

class LearningPathEvaluator:
    def __init__(self):
        self.evaluator = SystemEvaluator()
        self.metrics_history = []
    
    def evaluate_path_coherence(self, learning_path: List[Dict]) -> float:
        """Đánh giá tính liên kết của lộ trình học tập"""
        if not learning_path:
            return 0.0
            
        # Tính toán độ liên kết dựa trên các yếu tố:
        # 1. Sự phụ thuộc giữa các khóa học
        # 2. Độ khó tăng dần
        # 3. Tính liên tục của chủ đề
        
        coherence_scores = []
        
        for i in range(len(learning_path) - 1):
            current_course = learning_path[i]
            next_course = learning_path[i + 1]
            
            # Kiểm tra sự phụ thuộc
            if next_course.get('prerequisites', []) and current_course['id'] in next_course['prerequisites']:
                coherence_scores.append(1.0)
            else:
                coherence_scores.append(0.5)
            
            # Kiểm tra độ khó tăng dần
            if next_course.get('difficulty', 0) > current_course.get('difficulty', 0):
                coherence_scores.append(1.0)
            else:
                coherence_scores.append(0.5)
            
            # Kiểm tra tính liên tục của chủ đề
            current_topics = set(current_course.get('topics', []))
            next_topics = set(next_course.get('topics', []))
            topic_overlap = len(current_topics & next_topics) / len(current_topics | next_topics) if current_topics or next_topics else 0
            coherence_scores.append(topic_overlap)
        
        return np.mean(coherence_scores) if coherence_scores else 0.0
    
    def evaluate_path_completeness(self, 
                                 learning_path: List[Dict],
                                 user_goals: List[str]) -> float:
        """Đánh giá tính đầy đủ của lộ trình học tập"""
        if not learning_path or not user_goals:
            return 0.0
            
        # Kiểm tra xem lộ trình có bao quát được các mục tiêu của người dùng không
        covered_topics = set()
        for course in learning_path:
            covered_topics.update(course.get('topics', []))
        
        goal_coverage = []
        for goal in user_goals:
            # Giả sử mỗi mục tiêu có thể được map tới một số topics
            goal_topics = self._map_goal_to_topics(goal)
            coverage = len(covered_topics & set(goal_topics)) / len(goal_topics) if goal_topics else 0
            goal_coverage.append(coverage)
        
        return np.mean(goal_coverage) if goal_coverage else 0.0
    
    def evaluate_path_difficulty(self,
                               learning_path: List[Dict],
                               user_level: str) -> float:
        """Đánh giá độ phù hợp về độ khó của lộ trình"""
        if not learning_path:
            return 0.0
            
        # Map user level sang số
        level_map = {
            'beginner': 1,
            'intermediate': 2,
            'advanced': 3
        }
        user_level_num = level_map.get(user_level.lower(), 1)
        
        # Tính độ chênh lệch trung bình giữa độ khó của khóa học và trình độ người dùng
        difficulty_diffs = []
        for course in learning_path:
            course_difficulty = course.get('difficulty', 1)
            diff = abs(course_difficulty - user_level_num)
            difficulty_diffs.append(1.0 / (1.0 + diff))  # Chuyển đổi thành score (càng gần càng tốt)
        
        return np.mean(difficulty_diffs) if difficulty_diffs else 0.0
    
    def evaluate_path_duration(self,
                             learning_path: List[Dict],
                             user_time_constraint: int) -> float:
        """Đánh giá độ phù hợp về thời gian của lộ trình"""
        if not learning_path:
            return 0.0
            
        total_duration = sum(course.get('duration', 0) for course in learning_path)
        
        # Tính score dựa trên độ chênh lệch với thời gian người dùng có
        if total_duration <= user_time_constraint:
            return 1.0
        else:
            return max(0.0, 1.0 - (total_duration - user_time_constraint) / user_time_constraint)
    
    def evaluate_learning_path(self,
                             learning_path: List[Dict],
                             user_profile: Dict[str, Any]) -> Dict[str, float]:
        """Đánh giá toàn diện lộ trình học tập"""
        metrics = {
            'coherence': self.evaluate_path_coherence(learning_path),
            'completeness': self.evaluate_path_completeness(learning_path, user_profile.get('goals', [])),
            'difficulty_match': self.evaluate_path_difficulty(learning_path, user_profile.get('level', 'beginner')),
            'time_match': self.evaluate_path_duration(learning_path, user_profile.get('time_constraint', 0))
        }
        
        # Tính điểm tổng hợp
        metrics['overall_score'] = np.mean(list(metrics.values()))
        
        # Lưu metrics
        metrics['timestamp'] = datetime.now()
        self.metrics_history.append(metrics)
        
        return metrics
    
    def _map_goal_to_topics(self, goal: str) -> List[str]:
        """Map mục tiêu học tập sang các topics tương ứng"""
        # Đây là một mapping đơn giản, có thể mở rộng dựa trên nhu cầu
        goal_topic_map = {
            'learn python': ['python', 'programming', 'coding'],
            'learn machine learning': ['machine learning', 'data science', 'statistics'],
            'learn deep learning': ['deep learning', 'neural networks', 'machine learning'],
            'learn web development': ['web development', 'html', 'css', 'javascript'],
            'learn data structures': ['data structures', 'algorithms', 'computer science']
        }
        
        return goal_topic_map.get(goal.lower(), [])

# Ví dụ sử dụng
if __name__ == "__main__":
    evaluator = LearningPathEvaluator()
    
    # Tạo dữ liệu test
    test_learning_path = [
        {
            'id': 1,
            'title': 'Python Basics',
            'difficulty': 1,
            'duration': 20,
            'topics': ['python', 'programming'],
            'prerequisites': []
        },
        {
            'id': 2,
            'title': 'Data Structures in Python',
            'difficulty': 2,
            'duration': 30,
            'topics': ['python', 'data structures'],
            'prerequisites': [1]
        },
        {
            'id': 3,
            'title': 'Machine Learning Fundamentals',
            'difficulty': 2,
            'duration': 40,
            'topics': ['machine learning', 'python'],
            'prerequisites': [1, 2]
        }
    ]
    
    test_user_profile = {
        'goals': ['learn python', 'learn machine learning'],
        'level': 'beginner',
        'time_constraint': 100  # hours
    }
    
    # Đánh giá lộ trình
    metrics = evaluator.evaluate_learning_path(test_learning_path, test_user_profile)
    
    # In kết quả
    print("\nLearning Path Evaluation Results:")
    print("-" * 50)
    for metric_name, value in metrics.items():
        if metric_name != 'timestamp':
            print(f"{metric_name}: {value:.4f}") 