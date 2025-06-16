import time
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score
import pandas as pd
from datetime import datetime

class SystemEvaluator:
    def __init__(self):
        self.metrics_history = []
        
    def evaluate_response_time(self, start_time: float, end_time: float) -> float:
        """Đánh giá thời gian phản hồi của hệ thống"""
        return end_time - start_time
    
    def evaluate_rag_performance(self, 
                               retrieved_docs: List[Dict],
                               ground_truth_docs: List[Dict],
                               query: str) -> Dict[str, float]:
        """Đánh giá hiệu suất của RAG"""
        # Tính precision@k
        retrieved_ids = [doc['id'] for doc in retrieved_docs]
        ground_truth_ids = [doc['id'] for doc in ground_truth_docs]
        
        precision = len(set(retrieved_ids) & set(ground_truth_ids)) / len(retrieved_ids) if retrieved_ids else 0
        recall = len(set(retrieved_ids) & set(ground_truth_ids)) / len(ground_truth_ids) if ground_truth_ids else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def evaluate_answer_quality(self, 
                              generated_answer: str,
                              ground_truth: str) -> Dict[str, float]:
        """Đánh giá chất lượng câu trả lời"""
        # Tính similarity giữa câu trả lời được tạo và ground truth
        # Sử dụng cosine similarity cho embedding vectors
        # Giả sử chúng ta đã có hàm get_embeddings từ Cohere
        from cohere import Client
        co = Client('rk8CmFr7JMYSE55RC2NyUmiS5Nj7spZ6YBooQU25')
        
        gen_emb = co.embed([generated_answer]).embeddings[0]
        truth_emb = co.embed([ground_truth]).embeddings[0]
        
        similarity = cosine_similarity([gen_emb], [truth_emb])[0][0]
        
        return {
            'answer_similarity': similarity
        }
    
    def evaluate_learning_path(self,
                             generated_path: List[Dict],
                             user_feedback: Dict[str, Any]) -> Dict[str, float]:
        """Đánh giá chất lượng lộ trình học tập"""
        # Tính điểm dựa trên phản hồi người dùng
        relevance_score = user_feedback.get('relevance', 0)
        difficulty_score = user_feedback.get('difficulty_match', 0)
        completeness_score = user_feedback.get('completeness', 0)
        
        return {
            'relevance_score': relevance_score,
            'difficulty_match': difficulty_score,
            'completeness': completeness_score
        }
    
    def compare_with_baseline(self,
                            rag_results: Dict[str, float],
                            baseline_results: Dict[str, float]) -> Dict[str, float]:
        """So sánh kết quả RAG với baseline"""
        improvements = {}
        for metric in rag_results:
            if metric in baseline_results:
                improvements[metric] = rag_results[metric] - baseline_results[metric]
        
        return improvements
    
    def log_metrics(self, metrics: Dict[str, float]):
        """Lưu metrics vào lịch sử"""
        metrics['timestamp'] = datetime.now()
        self.metrics_history.append(metrics)
    
    def generate_report(self) -> pd.DataFrame:
        """Tạo báo cáo từ lịch sử metrics"""
        df = pd.DataFrame(self.metrics_history)
        return df.describe()

# Ví dụ sử dụng
if __name__ == "__main__":
    evaluator = SystemEvaluator()
    
    # Ví dụ đánh giá thời gian phản hồi
    start_time = time.time()
    # ... thực hiện các thao tác của hệ thống ...
    end_time = time.time()
    response_time = evaluator.evaluate_response_time(start_time, end_time)
    
    # Ví dụ đánh giá RAG
    retrieved_docs = [{'id': 1, 'content': 'doc1'}, {'id': 2, 'content': 'doc2'}]
    ground_truth_docs = [{'id': 1, 'content': 'doc1'}, {'id': 3, 'content': 'doc3'}]
    rag_metrics = evaluator.evaluate_rag_performance(retrieved_docs, ground_truth_docs, "test query")
    
    # Lưu metrics
    evaluator.log_metrics({
        'response_time': response_time,
        **rag_metrics
    })
    
    # Tạo báo cáo
    report = evaluator.generate_report()
    print(report) 