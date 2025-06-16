import os
import json
import logging
import re
import requests
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.schema import Document
from src.vector_store import VectorStore
import cohere

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LearningPathRAG:
    def __init__(self, courses_file="data/courses.json", cohere_api_key=None):
        """Khởi tạo hệ thống RAG"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Thiết lập logging
            self.logger = logging.getLogger(__name__)
            
            # Thiết lập API keys
            self.cohere_api_key = cohere_api_key or os.getenv("COHERE_API_KEY")
            if not self.cohere_api_key:
                raise ValueError("COHERE_API_KEY không được cung cấp")
            
            # Thiết lập Google API key
            self.google_api_key = os.getenv("GOOGLE_API_KEY")
            if not self.google_api_key:
                self.logger.warning("GOOGLE_API_KEY không được cung cấp, một số chức năng có thể không hoạt động")
            
            # Thiết lập đường dẫn file courses
            self.courses_file = courses_file
            
            # Tải dữ liệu khóa học
            self.courses = self.load_courses()
            
            # Khởi tạo Cohere client
            self.cohere_client = cohere.Client(api_key=self.cohere_api_key)
            
            # Khởi tạo vectorstore
            self.vectorstore = self.create_vector_store()
            
            logger.info("Khởi tạo LearningPathRAG thành công")
            
        except Exception as e:
            logger.error(f"Lỗi khởi tạo hệ thống RAG: {str(e)}")
            raise

    def load_courses(self):
        """Load courses from JSON file"""
        try:
            with open(self.courses_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                courses = data['courses']
                logger.info(f"Đã load {len(courses)} khóa học")
                return courses
        except Exception as e:
            logger.error(f"Lỗi load courses: {str(e)}")
            raise

    def create_vector_store(self):
        """Tạo vector store từ dữ liệu khóa học"""
        try:
            # Tạo text representations cho các khóa học
            texts = []
            metadatas = []
            for course in self.courses:
                # Tạo text representation chi tiết hơn
                text = f"""
                Khóa học: {course['title']}
                Mô tả: {course['description']}
                Chủ đề: {', '.join(course['topics'])}
                Cấp độ: {course['level']}
                Điều kiện tiên quyết: {', '.join(course['prerequisites']) if course['prerequisites'] else 'Không có'}
                Thời lượng: {course['duration']} tuần
                """
                
                # Thêm metadata để dễ dàng lọc và tìm kiếm
                metadata = {
                    'title': course['title'],
                    'level': course['level'],
                    'topics': course['topics'],
                    'duration': course['duration']
                }
                
                texts.append(text)
                metadatas.append(metadata)
            
            # Split texts thành chunks
            docs = [
                Document(page_content=text, metadata=metadata)
                for text, metadata in zip(texts, metadatas)
            ]
            
            # Tạo vector store
            vectorstore = VectorStore()
            
            logger.info("Đã tạo vector store thành công")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Lỗi tạo vector store: {str(e)}")
            return None

    def find_similar_courses(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Tìm kiếm khóa học phù hợp dựa trên câu truy vấn sử dụng Vector Store."""
        try:
            # Kiểm tra xem vectorstore có tồn tại không
            if self.vectorstore is None:
                logger.warning("Vector store là None, sẽ tạo mới vector store")
                try:
                    # Thử tạo lại vector store
                    self.create_vector_store()
                except Exception as ve:
                    logger.error(f"Không thể tạo vector store: {str(ve)}")
            
            # Thử sử dụng vector store để tìm khóa học
            if self.vectorstore is not None:
                logger.info(f"Tìm kiếm khóa học liên quan đến '{query}' sử dụng vector store")
                try:
                    search_results = self.vectorstore.search_courses(query, n_results=n_results)
                    if search_results:
                        logger.info(f"Đã tìm thấy {len(search_results)} khóa học liên quan")
                        return search_results
                except Exception as e:
                    logger.error(f"Lỗi khi tìm kiếm với vector store: {str(e)}")
            
            # Fallback: Tìm kiếm thủ công trong danh sách khóa học
            logger.warning(f"Sử dụng phương pháp tìm kiếm thủ công cho '{query}'")
            filtered_courses = []
            
            # Chuyển query về chữ thường để so sánh
            query_lower = query.lower()
            query_terms = query_lower.split()
            
            for course in self.courses:
                # Chuyển title và topics về chữ thường để so sánh
                course_title = course['title'].lower()
                course_topics = [topic.lower() for topic in course['topics']]
                course_description = course['description'].lower() if 'description' in course else ""
                
                # Tính điểm phù hợp
                score = 0
                
                # Nếu query hoàn toàn trùng với title
                if query_lower == course_title:
                    score += 5
                    
                # Nếu query là một phần của title
                elif query_lower in course_title:
                    score += 4
                
                # Nếu các từ trong query xuất hiện trong title
                for term in query_terms:
                    if term in course_title:
                        score += 3
                
                # Nếu query trùng với bất kỳ topic nào
                if any(query_lower == topic for topic in course_topics):
                    score += 4
                
                # Nếu query là một phần của bất kỳ topic nào
                elif any(query_lower in topic for topic in course_topics):
                    score += 3
                
                # Nếu các từ trong query xuất hiện trong topics
                for term in query_terms:
                    if any(term in topic for topic in course_topics):
                        score += 2
                
                # Nếu query xuất hiện trong description
                if query_lower in course_description:
                    score += 2
                
                # Nếu các từ trong query xuất hiện trong description
                for term in query_terms:
                    if term in course_description:
                        score += 1
                
                # Nếu có điểm phù hợp, thêm vào danh sách kết quả
                if score > 0:
                    course_info = {
                        "title": course['title'],
                        "level": course['level'],
                        "topics": course['topics'],
                        "duration": course['duration'],
                        "relevance_score": score / 10.0  # Chuẩn hóa về thang điểm 0-1
                    }
                    filtered_courses.append(course_info)
            
            # Sắp xếp kết quả theo điểm phù hợp giảm dần
            filtered_courses.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Giới hạn số lượng kết quả
            filtered_courses = filtered_courses[:n_results]
            
            logger.info(f"Tìm kiếm thủ công: Đã tìm thấy {len(filtered_courses)} khóa học liên quan")
            return filtered_courses
                
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm khóa học: {str(e)}")
            # Trong trường hợp lỗi xảy ra, trả về danh sách rỗng
            return []

    def create_learning_path(self, field: str, level: str, duration: int, daily_hours: int, interests: List[str]) -> Dict[str, Any]:
        """
        Tạo lộ trình học tập cá nhân hóa dựa trên các tham số đầu vào bằng cách sử dụng Gemini API.
        
        Args:
            field: Lĩnh vực học tập
            level: Trình độ (Beginner, Intermediate, Advanced)
            duration: Thời gian học tập (tháng)
            daily_hours: Số giờ học mỗi ngày
            interests: Danh sách các chủ đề quan tâm
            
        Returns:
            Dict chứa thông tin lộ trình học tập
        """
        try:
            # Kiểm tra API key
            if not self.google_api_key:
                logger.warning("GOOGLE_API_KEY không được cung cấp, sử dụng lộ trình dự phòng")
                relevant_courses = self.find_similar_courses(field, n_results=5)
                fallback_result = self.generate_fallback_learning_path(field, level, duration, daily_hours, interests, relevant_courses)
                if "learning_path" in fallback_result:
                    fallback_result["learning_path"]["is_fallback"] = True
                    fallback_result["learning_path"]["fallback_reason"] = "GOOGLE_API_KEY không được cung cấp"
                logger.info("Đã tạo lộ trình học tập fallback")
                return fallback_result
                
            logger.info(f"Bắt đầu tạo lộ trình học tập cho {field}, trình độ {level}")
            
            # Tìm các khóa học tương tự từ vector store
            courses_info = ""
            relevant_courses = []
            
            try:
                # Tìm các khóa học tương tự từ vector store
                relevant_courses = self.find_similar_courses(field, n_results=5)
                if relevant_courses:
                    courses_info = "Chúng tôi đã tìm thấy các khóa học sau đây trong cơ sở dữ liệu có thể liên quan đến yêu cầu của bạn:\n"
                    for i, course in enumerate(relevant_courses):
                        course_details = f"- {course.get('title', 'N/A')} (Cấp độ: {course.get('level', 'N/A')}, Thời lượng: {course.get('duration', 'N/A')} tuần"
                        topics = course.get('topics', [])
                        if topics:
                            course_details += f", Chủ đề chính: {', '.join(topics[:3])}"
                        course_details += ")\n"
                        courses_info += course_details
            except Exception as e:
                logger.warning(f"Không thể tìm khóa học tương tự: {str(e)}")
                courses_info = f"Không tìm thấy khóa học nào đặc biệt phù hợp cho {field}, {level} trong cơ sở dữ liệu."
            
            # Tạo prompt cho Gemini
            prompt = f"""
Yêu cầu: Tạo lộ trình học tập chi tiết bằng tiếng Việt cho lĩnh vực "{field}", trình độ {level}, trong vòng {duration} tháng, với thời gian học khoảng {daily_hours} giờ/ngày.
Người dùng có sở thích đặc biệt với: {', '.join(interests)}.

Thông tin tham khảo:
{courses_info}

Hướng dẫn tạo lộ trình:
1.  **Dựa chủ yếu** vào danh sách các khóa học tham khảo được cung cấp (nếu có). Hãy **ưu tiên lựa chọn và sắp xếp** các khóa học này vào lộ trình một cách hợp lý.
2.  Nếu danh sách tham khảo không đủ hoặc cần thiết để đảm bảo tính liền mạch, bạn có thể điều chỉnh nhẹ các khóa học (ví dụ: gộp chủ đề, thay đổi tên cho phù hợp với lộ trình) hoặc bổ sung các phần học/dự án nhỏ, nhưng hãy cố gắng **bám sát các khóa học gốc** nhất có thể.
3.  Lộ trình cần được chia thành các giai đoạn (phases) rõ ràng (ít nhất 3 giai đoạn).
4.  Lập kế hoạch chi tiết cho từng ngày (daily_plan) trong suốt thời gian học, phân bổ thời gian hợp lý cho các nhiệm vụ để đảm bảo đủ {daily_hours} giờ/ngày.
5.  Nội dung các nhiệm vụ học tập phải bằng tiếng Việt, đa dạng, phù hợp với chủ đề, trình độ và các sở thích đã nêu.
6.  Các ngày Chủ Nhật nên dành cho ôn tập, thực hành hoặc làm dự án nhỏ.
7.  Cung cấp tổng quan (overview), danh sách dự án gợi ý (projects), tài nguyên học tập (resources), và mẹo học tập (tips).

Định dạng Output:
Phản hồi của bạn PHẢI là một JSON object hợp lệ duy nhất, tuân thủ chính xác cấu trúc dưới đây và KHÔNG chứa bất kỳ văn bản giải thích nào khác bên ngoài JSON object.

```json
{{
  "learning_path": {{
    "field": "{field}",
    "level": "{level}",
    "duration": {duration},
    "daily_hours": {daily_hours},
    "interests": {json.dumps(interests, ensure_ascii=False)},
    "courses": [
      {{
        "title": "Tên khóa học được sử dụng/tạo ra trong lộ trình",
        "level": "Cấp độ", 
        "duration": 8, // Thời lượng ước tính (tuần)
        "topics": ["chủ đề 1", "chủ đề 2", "chủ đề 3"]
      }}
      // ... (các khóa học khác trong lộ trình)
    ],
    "phases": [
      {{
        "name": "Tên giai đoạn 1",
        "duration": 30, // Số ngày dự kiến
        "tasks": ["mô tả nhiệm vụ 1", "mô tả nhiệm vụ 2"] // Mô tả ngắn gọn các nhiệm vụ chính
      }}
      // ... (các giai đoạn khác)
    ],
    "daily_plan": [
      {{
        "date": "YYYY-MM-DD", // Ngày cụ thể
        "day_of_week": "Thứ/Ngày",
        "tasks": ["nhiệm vụ 1 (X.X giờ)", "nhiệm vụ 2 (Y.Y giờ)"] // Phân bổ thời gian cụ thể
      }}
      // ... (kế hoạch cho các ngày khác)
    ],
    "overview": "Tổng quan ngắn gọn về lộ trình học tập này.",
    "projects": ["Mô tả dự án gợi ý 1", "Mô tả dự án gợi ý 2"],
    "resources": ["Link hoặc tên tài nguyên hữu ích 1", "Tài nguyên 2"],
    "tips": ["Mẹo học tập hữu ích 1", "Mẹo 2"]
  }}
}}
```

Hãy đảm bảo JSON trả về là hợp lệ và đầy đủ các trường theo cấu trúc trên.
"""

            # Gọi Gemini API qua HTTP request
            try:
                logger.info("Gọi Gemini API để tạo lộ trình học tập")
                
                # Chuẩn bị request
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.google_api_key}"
                
                payload = {
                    "generationConfig": {
                        "temperature": 1.0,
                        "topP": 0.95,
                        "topK": 40,
                        "maxOutputTokens": 8192
                    },
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        }
                    ]
                }
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                # Gửi request và đo thời gian
                start_time = time.time()
                response = requests.post(url, json=payload, headers=headers)
                end_time = time.time()
                
                logger.info(f"Thời gian request Gemini: {end_time - start_time:.2f} giây")
                
                # Kiểm tra kết quả
                if response.status_code == 200:
                    logger.info("Request thành công!")
                    response_data = response.json()
                    
                    if "candidates" in response_data and len(response_data["candidates"]) > 0:
                        response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                        logger.info(f"Nhận được phản hồi từ Gemini API: {len(response_text)} ký tự")
                        
                        # Xử lý kết quả JSON
                        result = self.process_learning_path_json(response_text, field, level, duration, daily_hours, interests)
                        # Đánh dấu là kết quả thật từ API
                        if "learning_path" in result:
                            result["learning_path"]["is_fallback"] = False
                        return result
                    else:
                        logger.warning("Không nhận được phản hồi hợp lệ từ Gemini API, sử dụng lộ trình dự phòng")
                        fallback_result = self.generate_fallback_learning_path(field, level, duration, daily_hours, interests, relevant_courses)
                        # Đánh dấu là fallback
                        if "learning_path" in fallback_result:
                            fallback_result["learning_path"]["is_fallback"] = True
                            fallback_result["learning_path"]["fallback_reason"] = "Gemini API không trả về dữ liệu hợp lệ"
                        logger.info("Đã tạo lộ trình học tập fallback")
                        return fallback_result
                else:
                    logger.error(f"Request thất bại với mã lỗi: {response.status_code}")
                    logger.error(f"Thông báo lỗi: {response.text}")
                    
                    # Sử dụng fallback khi có lỗi HTTP
                    logger.warning(f"Sử dụng lộ trình dự phòng do lỗi API: {response.status_code}")
                    fallback_result = self.generate_fallback_learning_path(field, level, duration, daily_hours, interests, relevant_courses)
                    # Đánh dấu là fallback
                    if "learning_path" in fallback_result:
                        fallback_result["learning_path"]["is_fallback"] = True
                        fallback_result["learning_path"]["fallback_reason"] = f"Lỗi API HTTP {response.status_code}"
                    logger.info("Đã tạo lộ trình học tập fallback")
                    return fallback_result
                    
            except Exception as e:
                logger.error(f"Lỗi khi gọi Gemini API: {str(e)}")
                
                # Fallback: Tạo lộ trình học tập mặc định
                fallback_result = self.generate_fallback_learning_path(field, level, duration, daily_hours, interests, relevant_courses)
                # Đánh dấu là fallback
                if "learning_path" in fallback_result:
                    fallback_result["learning_path"]["is_fallback"] = True
                    fallback_result["learning_path"]["fallback_reason"] = f"Lỗi gọi API: {str(e)}"
                logger.info("Đã tạo lộ trình học tập fallback")
                return fallback_result
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo lộ trình học tập: {str(e)}")
            # Tạo một lộ trình mặc định đơn giản trong trường hợp lỗi nghiêm trọng
            fallback = {
                "learning_path": {
                    "field": field,
                    "level": level,
                    "duration": duration,
                    "daily_hours": daily_hours,
                    "interests": interests,
                    "is_fallback": True,
                    "fallback_reason": f"Lỗi nghiêm trọng: {str(e)}",
                    "courses": [],
                    "phases": [
                        {
                            "name": f"Nền tảng {field}",
                            "duration": 30,
                            "tasks": [f"Học cơ bản về {field}"]
                        }
                    ],
                    "daily_plan": [
                        {
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "day_of_week": "Ngày 1",
                            "tasks": [f"Bắt đầu học {field} ({daily_hours} giờ)"]
                        }
                    ],
                    "overview": f"Lộ trình học tập {field} cơ bản",
                    "projects": [],
                    "resources": [],
                    "tips": []
                }
            }
            return fallback

    def process_learning_path_json(self, response_text: str, field: str, level: str, duration: int, daily_hours: int, interests: List[str]) -> Dict[str, Any]:
        """
        Xử lý kết quả JSON từ phản hồi của Gemini API
        
        Args:
            response_text: Văn bản trả về từ Gemini API
            field, level, duration, daily_hours, interests: Các thông tin cơ bản
            
        Returns:
            Dict chứa thông tin lộ trình học tập đã parse
        """
        try:
            # Chuẩn bị cấu trúc mặc định
            default_json = {
                "learning_path": {
                    "field": field,
                    "level": level,
                    "duration": duration,
                    "daily_hours": daily_hours,
                    "interests": interests,
                    "courses": [],
                    "phases": [],
                    "daily_plan": [],
                    "overview": "",
                    "projects": [],
                    "resources": [],
                    "tips": []
                }
            }
            
            # Tìm phần JSON trong kết quả - Gemini thường trả về JSON trong code block
            json_str = ""
            
            # Trường hợp 1: JSON nằm trong code block ```json ... ```
            json_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_block_match:
                json_str = json_block_match.group(1)
                logger.info("Đã tìm thấy JSON trong code block")
            else:
                # Trường hợp 2: JSON không nằm trong code block
                start_pos = response_text.find('{')
                end_pos = response_text.rfind('}') + 1
                
                if start_pos >= 0 and end_pos > start_pos:
                    json_str = response_text[start_pos:end_pos]
                    logger.info("Đã tìm thấy JSON trong phản hồi")
            
            if json_str:
                logger.info(f"JSON được trích xuất (200 ký tự đầu): {json_str[:200]}")
                
                # Loại bỏ các kí tự không mong muốn
                json_str = json_str.replace('\n', ' ').replace('\r', '')
                
                # Thử phân tích JSON
                try:
                    json_data = json.loads(json_str)
                    logger.info("Phân tích JSON thành công")
                    
                    # Đảm bảo cấu trúc JSON đúng định dạng
                    if "learning_path" not in json_data:
                        logger.warning("Không tìm thấy trường 'learning_path' trong JSON, thử kiểm tra cấu trúc cấp cao hơn")
                        # JSON có thể không có cấu trúc nested đúng - kiểm tra các trường đặc trưng
                        if any(key in json_data for key in ["courses", "phases", "daily_plan", "overview"]):
                            json_data = {"learning_path": json_data}
                    
                    # Đảm bảo tất cả các trường cần thiết đều tồn tại
                    learning_path = json_data.get("learning_path", {})
                    for key in ["courses", "phases", "daily_plan", "projects", "resources", "tips"]:
                        if key not in learning_path:
                            learning_path[key] = []
                    
                    if "overview" not in learning_path:
                        learning_path["overview"] = ""
                    
                    # Bảo toàn các trường cơ bản
                    learning_path["field"] = field
                    learning_path["level"] = level
                    learning_path["duration"] = duration
                    learning_path["daily_hours"] = daily_hours
                    learning_path["interests"] = interests
                    
                    # Chuẩn hóa ngày tháng
                    try:
                        if "daily_plan" in learning_path and learning_path["daily_plan"]:
                            # Lấy ngày hiện tại
                            start_date = datetime.now()
                            
                            # Định dạng lại ngày trong daily_plan
                            for i, day in enumerate(learning_path["daily_plan"]):
                                # Tính toán ngày mới dựa trên chỉ số
                                new_date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                                # Gán ngày mới
                                day["date"] = new_date
                                
                                # Tính toán thứ trong tuần
                                weekday = (start_date + timedelta(days=i)).weekday()
                                day_of_week = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"][weekday]
                                day["day_of_week"] = day_of_week
                            
                            logger.info(f"Đã chuẩn hóa ngày tháng cho {len(learning_path['daily_plan'])} ngày")
                    except Exception as e:
                        logger.warning(f"Không thể chuẩn hóa ngày tháng: {str(e)}")
                    
                    json_data["learning_path"] = learning_path
                    
                    # Lưu JSON để debug
                    try:
                        with open("last_learning_path.json", "w", encoding="utf-8") as f:
                            json.dump(json_data, f, ensure_ascii=False, indent=2)
                        logger.info("Đã lưu JSON vào file last_learning_path.json")
                    except Exception as e:
                        logger.warning(f"Không thể lưu JSON ra file: {str(e)}")
                    
                    return json_data
                    
                except json.JSONDecodeError as je:
                    logger.warning(f"Lỗi parse JSON ban đầu: {str(je)}")
                    
                    # Thử cách làm sạch JSON
                    try:
                        # Sửa lỗi dấu phẩy thừa
                        json_str = re.sub(r',\s*}', '}', json_str)
                        json_str = re.sub(r',\s*]', ']', json_str)
                        
                        # Sửa các chuỗi JSON không hợp lệ
                        json_str = json_str.replace("'", '"')
                        # Thêm dấu ngoặc kép cho các khóa không có
                        json_str = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', json_str)
                        
                        logger.info(f"JSON sau khi làm sạch: {json_str[:200]}")
                        json_data = json.loads(json_str)
                        logger.info("Phân tích JSON thành công sau khi làm sạch")
                        
                        # Kiểm tra cấu trúc
                        if "learning_path" not in json_data:
                            json_data = {"learning_path": json_data}
                        
                        # Lưu JSON để debug
                        try:
                            with open("last_learning_path_cleaned.json", "w", encoding="utf-8") as f:
                                json.dump(json_data, f, ensure_ascii=False, indent=2)
                        except: pass
                        
                        return json_data
                    except Exception as e2:
                        logger.error(f"Vẫn không thể parse JSON sau khi làm sạch: {str(e2)}")
            else:
                logger.warning("Không tìm thấy cấu trúc JSON trong phản hồi")
            
            # Lưu phản hồi gốc vào file để debug
            try:
                with open("last_gemini_response.txt", "w", encoding="utf-8") as f:
                    f.write(response_text)
                logger.info("Đã lưu phản hồi gốc vào file last_gemini_response.txt")
            except Exception as e:
                logger.warning(f"Không thể lưu phản hồi gốc ra file: {str(e)}")
            
            return default_json
            
        except Exception as e:
            logger.error(f"Lỗi không mong đợi khi xử lý JSON: {str(e)}")
            return {
                "learning_path": {
                    "field": field,
                    "level": level,
                    "duration": duration, 
                    "daily_hours": daily_hours,
                    "interests": interests,
                    "courses": [],
                    "phases": [],
                    "daily_plan": [],
                    "overview": "",
                    "projects": [],
                    "resources": [],
                    "tips": []
                }
            }

    def generate_fallback_learning_path(self, field: str, level: str, duration: int, daily_hours: int, interests: List[str], relevant_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Tạo lộ trình học tập mặc định khi không thành công với Gemini API
        
        Args:
            field, level, duration, daily_hours, interests: Các thông tin cơ bản
            relevant_courses: Danh sách các khóa học liên quan
            
        Returns:
            Dict chứa thông tin lộ trình học tập mặc định
        """
        try:
            logger.info(f"Sử dụng lộ trình học tập dự phòng cho {field}")
            
            # Tạo kế hoạch học tập hàng ngày chi tiết trong trường hợp fallback
            start_date = datetime.now()
            
            # Tạo lộ trình học tập dự phòng
            fallback_learning_path = {
                "field": field,
                "level": level,
                "duration": duration,
                "daily_hours": daily_hours,
                "interests": interests,
                "overview": f"Lộ trình học tập {field} dành cho trình độ {level} trong {duration} tháng",
                "courses": [],
                "phases": [
                    {
                        "name": f"Nền tảng {field}",
                        "duration": duration * 10,
                        "tasks": [f"Học cơ bản về {field}", f"Làm quen với các công cụ {field}"]
                    },
                    {
                        "name": f"Thực hành {field}",
                        "duration": duration * 10,
                        "tasks": [f"Thực hành các kỹ năng {field}", f"Xây dựng dự án nhỏ về {field}"]
                    },
                    {
                        "name": f"Nâng cao {field}",
                        "duration": duration * 10,
                        "tasks": [f"Học các kỹ thuật nâng cao về {field}", f"Hoàn thiện dự án cuối khóa"]
                    }
                ],
                "daily_plan": [],
                "projects": [f"Dự án cơ bản về {field}", f"Dự án nâng cao về {field}"],
                "resources": [f"Sách về {field}", f"Khóa học online về {field}", f"Trang web tham khảo về {field}"],
                "tips": [
                    "Hãy học đều đặn mỗi ngày",
                    "Thực hành là cách học hiệu quả nhất",
                    "Tham gia cộng đồng để trao đổi kinh nghiệm",
                    "Xây dựng dự án thực tế để áp dụng kiến thức"
                ]
            }
            
            # Thêm khóa học từ kết quả tìm kiếm
            if relevant_courses:
                for course in relevant_courses[:3]:
                    course_duration = 4
                    if 'duration' in course:
                        try:
                            course_duration = int(course['duration'])
                        except (ValueError, TypeError):
                            course_duration = 4
                    
                    fallback_learning_path["courses"].append({
                        "title": course["title"],
                        "level": course["level"],
                        "duration": course_duration,
                        "topics": course.get("topics", [])[:5]
                    })
            
            # Danh sách các kỹ năng dựa theo lĩnh vực
            field_topics = self.generate_field_specific_topics(field, interests)
            
            # Danh sách nhiệm vụ dựa theo cấp độ
            level_tasks = self.generate_level_specific_tasks(level, field)
            
            # Tạo kế hoạch chi tiết theo từng ngày
            for day in range(duration * 30):  # Ước tính 30 ngày mỗi tháng
                current_date = start_date + timedelta(days=day)
                weekday = current_date.weekday()
                day_of_week = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"][weekday]
                
                # Tính toán giai đoạn hiện tại để tạo nội dung phù hợp
                phase = min(day // 30 + 1, 3)  # Giai đoạn 1, 2, hoặc 3
                
                # Tạo các nhiệm vụ học tập phù hợp với giai đoạn và trình độ
                if weekday == 6:  # Chủ nhật
                    if phase == 1:
                        tasks = [
                            f"Ôn tập kiến thức cơ bản về {field_topics[day % len(field_topics)]} ({daily_hours/2} giờ)",
                            f"Làm bài tập thực hành về {field_topics[(day+1) % len(field_topics)]} ({daily_hours/2} giờ)"
                        ]
                    elif phase == 2:
                        tasks = [
                            f"Ôn tập và tổng hợp kiến thức tuần trước ({daily_hours/3} giờ)",
                            f"Thực hành dự án nhỏ về {field_topics[(day+2) % len(field_topics)]} ({daily_hours/3} giờ)",
                            f"Lập kế hoạch học tập cho tuần mới ({daily_hours/3} giờ)"
                        ]
                    else:
                        tasks = [
                            f"Đánh giá tiến độ dự án ({daily_hours/3} giờ)",
                            f"Thực hành nâng cao về {field_topics[(day+3) % len(field_topics)]} ({daily_hours/3} giờ)",
                            f"Chuẩn bị nội dung thuyết trình dự án ({daily_hours/3} giờ)"
                        ]
                else:
                    # Ngày thường
                    if phase == 1:
                        time_per_task = daily_hours / 2
                        tasks = [
                            f"Học lý thuyết về {field_topics[day % len(field_topics)]} ({time_per_task} giờ)",
                            f"Thực hành {level_tasks[day % len(level_tasks)]} ({time_per_task} giờ)"
                        ]
                    elif phase == 2:
                        time_per_task = daily_hours / 3
                        tasks = [
                            f"Học kỹ thuật {field_topics[(day+1) % len(field_topics)]} ({time_per_task} giờ)",
                            f"Ứng dụng {level_tasks[(day+1) % len(level_tasks)]} ({time_per_task} giờ)",
                            f"Nghiên cứu tình huống thực tế về {field_topics[(day+2) % len(field_topics)]} ({time_per_task} giờ)"
                        ]
                    else:
                        time_per_task = daily_hours / 3
                        tasks = [
                            f"Học nâng cao về {field_topics[(day+3) % len(field_topics)]} ({time_per_task} giờ)",
                            f"Phát triển dự án ứng dụng {field_topics[(day+4) % len(field_topics)]} ({time_per_task} giờ)",
                            f"Giải quyết vấn đề phức tạp trong {field_topics[(day+5) % len(field_topics)]} ({time_per_task} giờ)"
                        ]
                
                fallback_learning_path["daily_plan"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day_of_week": day_of_week,
                    "tasks": tasks
                })
            
            return {"learning_path": fallback_learning_path}
            
        except Exception as e:
            logger.error(f"Lỗi không xác định khi tạo lộ trình học tập: {str(e)}")
            return {
                "learning_path": {
                    "field": field,
                    "level": level,
                    "duration": duration,
                    "daily_hours": daily_hours,
                    "interests": interests,
                    "courses": [],
                    "phases": [],
                    "daily_plan": [],
                    "overview": "",
                    "projects": [],
                    "resources": [],
                    "tips": []
                }
            }

    def generate_field_specific_topics(self, field: str, interests: List[str]) -> List[str]:
        """
        Tạo danh sách các chủ đề cụ thể dựa trên lĩnh vực và sở thích
        """
        base_topics = []
        
        # Chủ đề chung
        generic_topics = [
            "cấu trúc dữ liệu", "thuật toán", "lập trình hướng đối tượng", 
            "thiết kế phần mềm", "quản lý dự án", "kiến trúc ứng dụng",
            "tối ưu hóa mã nguồn", "kiểm thử phần mềm", "phương pháp agile"
        ]
        
        # Thêm chủ đề dựa trên lĩnh vực
        if "python" in field.lower():
            base_topics.extend([
                "cú pháp Python", "kiểu dữ liệu trong Python", "vòng lặp và điều kiện", 
                "hàm và module", "xử lý ngoại lệ", "làm việc với file", 
                "thư viện numpy", "pandas", "matplotlib", "OOP trong Python",
                "list comprehension", "generator", "decorator", "lambda function",
                "regular expression", "virtual environment", "pip"
            ])
        elif "java" in field.lower():
            base_topics.extend([
                "cú pháp Java", "kiểu dữ liệu trong Java", "cấu trúc điều khiển", 
                "OOP trong Java", "interface và abstract class", "collection framework", 
                "xử lý ngoại lệ", "multithreading", "generic", "annotation",
                "stream API", "lambda expression", "JavaFX", "JDBC", "Servlet"
            ])
        elif "javascript" in field.lower() or "js" in field.lower():
            base_topics.extend([
                "cú pháp JavaScript", "DOM manipulation", "event handling", 
                "ES6 features", "promise", "async/await", "callback", 
                "closure", "scope", "hoisting", "prototype", "JSON",
                "localStorage", "sessionStorage", "AJAX", "fetch API"
            ])
        elif "web" in field.lower():
            base_topics.extend([
                "HTML", "CSS", "JavaScript", "responsive design", "CSS framework", 
                "frontend framework", "backend development", "REST API", 
                "authentication", "database design", "web security"
            ])
        elif "data" in field.lower():
            base_topics.extend([
                "SQL", "NoSQL", "data cleaning", "data visualization", 
                "statistical analysis", "machine learning", "big data", 
                "data pipeline", "ETL", "data warehousing", "BI tools"
            ])
        elif "mobile" in field.lower():
            base_topics.extend([
                "native development", "cross-platform development", "UI/UX design", 
                "state management", "API integration", "local storage", 
                "push notification", "app deployment", "responsive design"
            ])
        
        # Thêm chủ đề dựa trên sở thích
        for interest in interests:
            if "web" in interest.lower():
                base_topics.extend(["framework React", "Vue.js", "Angular", "Node.js", "Express", "Django", "Laravel"])
            elif "data" in interest.lower():
                base_topics.extend(["phân tích dữ liệu", "học máy", "deep learning", "trực quan hóa dữ liệu", "pandas", "sklearn"])
            elif "automation" in interest.lower():
                base_topics.extend(["tự động hóa quy trình", "CI/CD", "scripting", "testing automation", "RPA"])
            elif "game" in interest.lower():
                base_topics.extend(["game engine", "thiết kế game", "lập trình game", "3D modeling", "game physics"])
        
        # Kết hợp các chủ đề và loại bỏ trùng lặp
        all_topics = list(set(base_topics + generic_topics))
        
        # Nếu không có chủ đề nào thì sử dụng generic topics
        if not all_topics:
            return generic_topics
            
        return all_topics
    
    def generate_level_specific_tasks(self, level: str, field: str) -> List[str]:
        """
        Tạo danh sách các nhiệm vụ cụ thể dựa trên cấp độ và lĩnh vực
        """
        tasks = []
        
        # Nhiệm vụ cho người mới bắt đầu
        if level.lower() in ["beginner", "cơ bản", "basic", "beginer", "newbie"]:
            tasks = [
                f"cài đặt môi trường phát triển cho {field}",
                f"thực hành cú pháp cơ bản trong {field}",
                f"làm quen với IDE/editor cho {field}",
                f"giải các bài tập cơ bản về {field}",
                f"làm mini-project đơn giản về {field}",
                f"đọc tài liệu cơ bản về {field}",
                f"xem video hướng dẫn về {field}",
                f"làm bài tập về cấu trúc dữ liệu đơn giản",
                f"viết mã theo hướng đối tượng đơn giản",
                f"debug lỗi cơ bản",
                f"ghi chú và tổng hợp kiến thức",
                f"chia sẻ mã nguồn lên GitHub"
            ]
        
        # Nhiệm vụ cho người có kinh nghiệm
        elif level.lower() in ["intermediate", "trung cấp", "trung bình"]:
            tasks = [
                f"áp dụng design pattern trong {field}",
                f"tối ưu hóa mã nguồn cho {field}",
                f"viết test cho mã nguồn {field}",
                f"tìm hiểu framework phổ biến cho {field}",
                f"đọc mã nguồn mở về {field}",
                f"tham gia dự án nhóm về {field}",
                f"tạo REST API cho ứng dụng {field}",
                f"tách biệt các thành phần trong ứng dụng",
                f"triển khai ứng dụng lên cloud",
                f"tích hợp third-party API",
                f"thiết kế database hiệu quả",
                f"tìm hiểu security best practices"
            ]
        
        # Nhiệm vụ cho người giỏi
        else:  # Advanced, expert, etc.
            tasks = [
                f"thiết kế kiến trúc phức tạp cho ứng dụng {field}",
                f"triển khai microservices cho {field}",
                f"tối ưu hóa hiệu suất ứng dụng {field}",
                f"xây dựng framework/thư viện cho {field}",
                f"viết technical blog về {field}",
                f"đóng góp cho dự án mã nguồn mở về {field}",
                f"triển khai CI/CD pipeline",
                f"thực hiện security audit",
                f"tạo high-performance system",
                f"đánh giá và cải thiện UX/UI",
                f"thiết kế và triển khai distributed system",
                f"nghiên cứu kỹ thuật mới cho {field}"
            ]
        
        return tasks