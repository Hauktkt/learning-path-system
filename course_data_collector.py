import requests
import pandas as pd
from typing import List, Dict, Any
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import time
from udemy_auth import UdemyAuth
from config import UDEMY_API_CONFIG, COURSERA_API_CONFIG, EDX_API_CONFIG, KHAN_ACADEMY_API_CONFIG

class CourseDataCollector:
    def __init__(self, data_file: str = "course_database.json"):
        self.data_file = data_file
        self.courses = self._load_data()
        self.udemy_auth = UdemyAuth()
        
        # Các nguồn dữ liệu uy tín
        self.sources = {
            'coursera': COURSERA_API_CONFIG,
            'edx': EDX_API_CONFIG,
            'udemy': UDEMY_API_CONFIG,
            'khan_academy': KHAN_ACADEMY_API_CONFIG
        }
    
    def _load_data(self) -> List[Dict]:
        """Load existing course data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_data(self):
        """Save course data to file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.courses, f, ensure_ascii=False, indent=2)
    
    def collect_coursera_courses(self, subject: str = None, limit: int = 100):
        """Thu thập khóa học từ Coursera"""
        try:
            params = {
                'q': 'search',
                'query': subject if subject else '',
                'limit': limit
            }
            
            response = requests.get(
                f"{self.sources['coursera']['api_url']}/search",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                for course in data.get('elements', []):
                    course_data = {
                        'source': 'coursera',
                        'id': course.get('id'),
                        'title': course.get('name'),
                        'description': course.get('description'),
                        'instructor': course.get('instructorIds', []),
                        'rating': course.get('averageRating'),
                        'enrollment_count': course.get('enrollmentCount'),
                        'difficulty': course.get('difficultyLevel'),
                        'duration': course.get('estimatedWorkload'),
                        'topics': course.get('categories', []),
                        'url': f"{self.sources['coursera']['base_url']}/learn/{course.get('slug')}",
                        'collected_at': datetime.now().isoformat()
                    }
                    self.courses.append(course_data)
                self._save_data()
                return True
        except Exception as e:
            print(f"Error collecting Coursera courses: {str(e)}")
        return False
    
    def collect_edx_courses(self, subject: str = None, limit: int = 100):
        """Thu thập khóa học từ edX"""
        try:
            params = {
                'search': subject if subject else '',
                'limit': limit
            }
            
            response = requests.get(
                f"{self.sources['edx']['api_url']}/catalogs",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                for course in data.get('results', []):
                    course_data = {
                        'source': 'edx',
                        'id': course.get('key'),
                        'title': course.get('title'),
                        'description': course.get('short_description'),
                        'instructor': course.get('staff', []),
                        'rating': course.get('rating'),
                        'enrollment_count': course.get('enrollment_count'),
                        'difficulty': course.get('level'),
                        'duration': course.get('effort'),
                        'topics': course.get('subjects', []),
                        'url': course.get('marketing_url'),
                        'collected_at': datetime.now().isoformat()
                    }
                    self.courses.append(course_data)
                self._save_data()
                return True
        except Exception as e:
            print(f"Error collecting edX courses: {str(e)}")
        return False
    
    def collect_udemy_courses(self, subject: str = None, limit: int = 100):
        """Thu thập khóa học từ Udemy"""
        try:
            params = {
                'search': subject if subject else '',
                'page_size': limit
            }
            
            headers = self.udemy_auth.get_auth_header()
            if not headers:
                print("Failed to get Udemy authentication headers")
                return False
            
            response = requests.get(
                f"{self.sources['udemy']['base_url']}/courses/",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                for course in data.get('results', []):
                    course_data = {
                        'source': 'udemy',
                        'id': course.get('id'),
                        'title': course.get('title'),
                        'description': course.get('description'),
                        'instructor': course.get('visible_instructors', []),
                        'rating': course.get('rating'),
                        'enrollment_count': course.get('num_subscribers'),
                        'difficulty': course.get('instructional_level'),
                        'duration': course.get('content_info'),
                        'topics': course.get('category', {}).get('title', ''),
                        'url': f"{self.sources['udemy']['base_url']}/course/{course.get('url')}",
                        'collected_at': datetime.now().isoformat()
                    }
                    self.courses.append(course_data)
                self._save_data()
                return True
            else:
                print(f"Error collecting Udemy courses: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error collecting Udemy courses: {str(e)}")
        return False
    
    def collect_khan_academy_courses(self, subject: str = None):
        """Thu thập khóa học từ Khan Academy"""
        try:
            response = requests.get(self.sources['khan_academy']['api_url'])
            
            if response.status_code == 200:
                data = response.json()
                for topic in data:
                    if subject and subject.lower() not in topic.get('title', '').lower():
                        continue
                        
                    course_data = {
                        'source': 'khan_academy',
                        'id': topic.get('id'),
                        'title': topic.get('title'),
                        'description': topic.get('description'),
                        'instructor': 'Khan Academy',
                        'rating': None,
                        'enrollment_count': None,
                        'difficulty': topic.get('level'),
                        'duration': None,
                        'topics': [topic.get('title')],
                        'url': f"{self.sources['khan_academy']['base_url']}{topic.get('url')}",
                        'collected_at': datetime.now().isoformat()
                    }
                    self.courses.append(course_data)
                self._save_data()
                return True
        except Exception as e:
            print(f"Error collecting Khan Academy courses: {str(e)}")
        return False
    
    def get_course_metrics(self) -> Dict[str, Any]:
        """Tính toán các metrics từ dữ liệu khóa học"""
        if not self.courses:
            return {}
        
        df = pd.DataFrame(self.courses)
        
        metrics = {
            'total_courses': len(df),
            'courses_by_source': df['source'].value_counts().to_dict(),
            'avg_rating_by_source': df.groupby('source')['rating'].mean().to_dict(),
            'top_topics': df['topics'].explode().value_counts().head(10).to_dict(),
            'difficulty_distribution': df['difficulty'].value_counts().to_dict()
        }
        
        return metrics
    
    def generate_course_report(self) -> pd.DataFrame:
        """Tạo báo cáo chi tiết về khóa học"""
        if not self.courses:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.courses)
        df['collected_at'] = pd.to_datetime(df['collected_at'])
        
        # Tạo báo cáo theo nguồn và thời gian
        report = df.sort_values(['source', 'collected_at'])
        
        return report

# Ví dụ sử dụng
if __name__ == "__main__":
    collector = CourseDataCollector()
    
    # Thu thập khóa học từ các nguồn
    print("Collecting courses from Coursera...")
    collector.collect_coursera_courses(subject="python programming", limit=50)
    
    print("Collecting courses from edX...")
    collector.collect_edx_courses(subject="python", limit=50)
    
    print("Collecting courses from Udemy...")
    collector.collect_udemy_courses(subject="python", limit=50)
    
    print("Collecting courses from Khan Academy...")
    collector.collect_khan_academy_courses(subject="computer science")
    
    # In kết quả
    print("\nCourse Metrics:")
    print(json.dumps(collector.get_course_metrics(), indent=2))
    
    print("\nDetailed Report:")
    print(collector.generate_course_report()) 