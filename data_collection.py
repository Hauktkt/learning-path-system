import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import os

class DataCollector:
    def __init__(self, data_file: str = "user_evaluations.json"):
        self.data_file = data_file
        self.evaluations = self._load_data()
    
    def _load_data(self) -> List[Dict]:
        """Load existing evaluation data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_data(self):
        """Save evaluation data to file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.evaluations, f, ensure_ascii=False, indent=2)
    
    def collect_user_feedback(self,
                            user_id: str,
                            learning_path: List[Dict],
                            user_profile: Dict[str, Any],
                            feedback: Dict[str, Any]):
        """Thu thập phản hồi từ người dùng"""
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'user_profile': user_profile,
            'learning_path': learning_path,
            'feedback': {
                'relevance': feedback.get('relevance', 0),  # 1-5
                'difficulty_match': feedback.get('difficulty_match', 0),  # 1-5
                'completeness': feedback.get('completeness', 0),  # 1-5
                'time_commitment': feedback.get('time_commitment', 0),  # 1-5
                'overall_satisfaction': feedback.get('overall_satisfaction', 0),  # 1-5
                'comments': feedback.get('comments', '')
            }
        }
        
        self.evaluations.append(evaluation)
        self._save_data()
    
    def collect_expert_evaluation(self,
                                expert_id: str,
                                learning_path: List[Dict],
                                user_profile: Dict[str, Any],
                                evaluation: Dict[str, Any]):
        """Thu thập đánh giá từ chuyên gia"""
        expert_eval = {
            'timestamp': datetime.now().isoformat(),
            'expert_id': expert_id,
            'user_profile': user_profile,
            'learning_path': learning_path,
            'evaluation': {
                'content_quality': evaluation.get('content_quality', 0),  # 1-5
                'learning_progression': evaluation.get('learning_progression', 0),  # 1-5
                'prerequisite_coverage': evaluation.get('prerequisite_coverage', 0),  # 1-5
                'topic_coverage': evaluation.get('topic_coverage', 0),  # 1-5
                'difficulty_progression': evaluation.get('difficulty_progression', 0),  # 1-5
                'comments': evaluation.get('comments', '')
            }
        }
        
        self.evaluations.append(expert_eval)
        self._save_data()
    
    def get_evaluation_metrics(self) -> Dict[str, float]:
        """Tính toán các metrics từ dữ liệu đánh giá"""
        if not self.evaluations:
            return {}
        
        df = pd.DataFrame(self.evaluations)
        
        # Tính trung bình các metrics
        metrics = {}
        
        # Metrics từ phản hồi người dùng
        user_feedback = df[df['feedback'].notna()]
        if not user_feedback.empty:
            feedback_metrics = {
                'avg_relevance': user_feedback['feedback'].apply(lambda x: x.get('relevance', 0)).mean(),
                'avg_difficulty_match': user_feedback['feedback'].apply(lambda x: x.get('difficulty_match', 0)).mean(),
                'avg_completeness': user_feedback['feedback'].apply(lambda x: x.get('completeness', 0)).mean(),
                'avg_time_commitment': user_feedback['feedback'].apply(lambda x: x.get('time_commitment', 0)).mean(),
                'avg_satisfaction': user_feedback['feedback'].apply(lambda x: x.get('overall_satisfaction', 0)).mean()
            }
            metrics.update(feedback_metrics)
        
        # Metrics từ đánh giá chuyên gia
        expert_evals = df[df['evaluation'].notna()]
        if not expert_evals.empty:
            expert_metrics = {
                'avg_content_quality': expert_evals['evaluation'].apply(lambda x: x.get('content_quality', 0)).mean(),
                'avg_learning_progression': expert_evals['evaluation'].apply(lambda x: x.get('learning_progression', 0)).mean(),
                'avg_prerequisite_coverage': expert_evals['evaluation'].apply(lambda x: x.get('prerequisite_coverage', 0)).mean(),
                'avg_topic_coverage': expert_evals['evaluation'].apply(lambda x: x.get('topic_coverage', 0)).mean(),
                'avg_difficulty_progression': expert_evals['evaluation'].apply(lambda x: x.get('difficulty_progression', 0)).mean()
            }
            metrics.update(expert_metrics)
        
        return metrics
    
    def generate_evaluation_report(self) -> pd.DataFrame:
        """Tạo báo cáo đánh giá chi tiết"""
        if not self.evaluations:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.evaluations)
        
        # Tạo báo cáo theo thời gian
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Tính toán các metrics theo thời gian
        report = pd.DataFrame()
        
        # Metrics từ phản hồi người dùng
        user_feedback = df[df['feedback'].notna()]
        if not user_feedback.empty:
            feedback_metrics = pd.DataFrame({
                'timestamp': user_feedback['timestamp'],
                'relevance': user_feedback['feedback'].apply(lambda x: x.get('relevance', 0)),
                'difficulty_match': user_feedback['feedback'].apply(lambda x: x.get('difficulty_match', 0)),
                'completeness': user_feedback['feedback'].apply(lambda x: x.get('completeness', 0)),
                'time_commitment': user_feedback['feedback'].apply(lambda x: x.get('time_commitment', 0)),
                'satisfaction': user_feedback['feedback'].apply(lambda x: x.get('overall_satisfaction', 0))
            })
            report = pd.concat([report, feedback_metrics])
        
        # Metrics từ đánh giá chuyên gia
        expert_evals = df[df['evaluation'].notna()]
        if not expert_evals.empty:
            expert_metrics = pd.DataFrame({
                'timestamp': expert_evals['timestamp'],
                'content_quality': expert_evals['evaluation'].apply(lambda x: x.get('content_quality', 0)),
                'learning_progression': expert_evals['evaluation'].apply(lambda x: x.get('learning_progression', 0)),
                'prerequisite_coverage': expert_evals['evaluation'].apply(lambda x: x.get('prerequisite_coverage', 0)),
                'topic_coverage': expert_evals['evaluation'].apply(lambda x: x.get('topic_coverage', 0)),
                'difficulty_progression': expert_evals['evaluation'].apply(lambda x: x.get('difficulty_progression', 0))
            })
            report = pd.concat([report, expert_metrics])
        
        return report.sort_values('timestamp')

# Ví dụ sử dụng
if __name__ == "__main__":
    collector = DataCollector()
    
    # Thu thập phản hồi từ người dùng
    user_feedback = {
        'relevance': 4,
        'difficulty_match': 3,
        'completeness': 4,
        'time_commitment': 3,
        'overall_satisfaction': 4,
        'comments': 'Lộ trình học tập rất phù hợp với mục tiêu của tôi'
    }
    
    collector.collect_user_feedback(
        user_id="user123",
        learning_path=[
            {
                'id': 1,
                'title': 'Python Basics',
                'difficulty': 1,
                'duration': 20,
                'topics': ['python', 'programming']
            }
        ],
        user_profile={
            'goals': ['learn python'],
            'level': 'beginner',
            'time_constraint': 100
        },
        feedback=user_feedback
    )
    
    # Thu thập đánh giá từ chuyên gia
    expert_evaluation = {
        'content_quality': 4,
        'learning_progression': 5,
        'prerequisite_coverage': 4,
        'topic_coverage': 4,
        'difficulty_progression': 3,
        'comments': 'Lộ trình có cấu trúc tốt và phù hợp với người mới bắt đầu'
    }
    
    collector.collect_expert_evaluation(
        expert_id="expert456",
        learning_path=[
            {
                'id': 1,
                'title': 'Python Basics',
                'difficulty': 1,
                'duration': 20,
                'topics': ['python', 'programming']
            }
        ],
        user_profile={
            'goals': ['learn python'],
            'level': 'beginner',
            'time_constraint': 100
        },
        evaluation=expert_evaluation
    )
    
    # In kết quả đánh giá
    print("\nEvaluation Metrics:")
    print(collector.get_evaluation_metrics())
    
    print("\nDetailed Report:")
    print(collector.generate_evaluation_report()) 