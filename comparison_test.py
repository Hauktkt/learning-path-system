import time
from typing import List, Dict
import numpy as np
from evaluation import SystemEvaluator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class BaselineRetriever:
    def __init__(self, method: str = 'tfidf'):
        self.method = method
        self.vectorizer = TfidfVectorizer() if method == 'tfidf' else None
        
    def retrieve(self, query: str, documents: List[Dict]) -> List[Dict]:
        if self.method == 'tfidf':
            return self._tfidf_retrieve(query, documents)
        elif self.method == 'random':
            return self._random_retrieve(documents)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _tfidf_retrieve(self, query: str, documents: List[Dict]) -> List[Dict]:
        # Chuyển đổi documents thành list of strings
        doc_texts = [doc['content'] for doc in documents]
        doc_texts.append(query)
        
        # Tính TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform(doc_texts)
        
        # Tính similarity giữa query và documents
        query_vector = tfidf_matrix[-1]
        doc_vectors = tfidf_matrix[:-1]
        similarities = cosine_similarity(query_vector, doc_vectors)[0]
        
        # Sắp xếp và trả về top k documents
        top_k = 3
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [documents[i] for i in top_indices]
    
    def _random_retrieve(self, documents: List[Dict]) -> List[Dict]:
        # Trả về ngẫu nhiên k documents
        k = 3
        indices = np.random.choice(len(documents), k, replace=False)
        return [documents[i] for i in indices]

def run_comparison_test():
    # Khởi tạo evaluator
    evaluator = SystemEvaluator()
    
    # Tạo dữ liệu test
    test_documents = [
        {'id': 1, 'content': 'Python programming basics'},
        {'id': 2, 'content': 'Machine learning fundamentals'},
        {'id': 3, 'content': 'Deep learning with neural networks'},
        {'id': 4, 'content': 'Data structures and algorithms'},
        {'id': 5, 'content': 'Natural language processing'},
    ]
    
    test_queries = [
        'How to learn machine learning?',
        'What are the basics of programming?',
        'How to start with deep learning?'
    ]
    
    # Ground truth cho mỗi query
    ground_truth = {
        'How to learn machine learning?': [2, 5],  # ML fundamentals và NLP
        'What are the basics of programming?': [1, 4],  # Python basics và Data structures
        'How to start with deep learning?': [2, 3]  # ML fundamentals và Deep learning
    }
    
    # Khởi tạo các phương pháp retrieval
    methods = {
        'rag': None,  # Giả sử RAG đã được implement
        'tfidf': BaselineRetriever(method='tfidf'),
        'random': BaselineRetriever(method='random')
    }
    
    results = {}
    
    # Chạy thử nghiệm cho mỗi phương pháp
    for method_name, retriever in methods.items():
        method_results = []
        
        for query in test_queries:
            start_time = time.time()
            
            if method_name == 'rag':
                # Giả sử RAG retrieval đã được implement
                retrieved_docs = []  # Implement RAG retrieval here
            else:
                retrieved_docs = retriever.retrieve(query, test_documents)
            
            end_time = time.time()
            
            # Đánh giá kết quả
            ground_truth_docs = [doc for doc in test_documents if doc['id'] in ground_truth[query]]
            metrics = evaluator.evaluate_rag_performance(retrieved_docs, ground_truth_docs, query)
            metrics['response_time'] = end_time - start_time
            
            method_results.append(metrics)
        
        # Tính trung bình các metrics
        avg_metrics = {
            'precision': np.mean([r['precision'] for r in method_results]),
            'recall': np.mean([r['recall'] for r in method_results]),
            'f1_score': np.mean([r['f1_score'] for r in method_results]),
            'response_time': np.mean([r['response_time'] for r in method_results])
        }
        
        results[method_name] = avg_metrics
    
    # In kết quả so sánh
    print("\nComparison Results:")
    print("-" * 50)
    for method, metrics in results.items():
        print(f"\n{method.upper()}:")
        for metric_name, value in metrics.items():
            print(f"{metric_name}: {value:.4f}")
    
    # So sánh RAG với baseline
    if 'rag' in results and 'tfidf' in results:
        improvements = evaluator.compare_with_baseline(results['rag'], results['tfidf'])
        print("\nRAG Improvements over TF-IDF:")
        for metric, improvement in improvements.items():
            print(f"{metric}: {improvement:.4f}")

if __name__ == "__main__":
    run_comparison_test() 