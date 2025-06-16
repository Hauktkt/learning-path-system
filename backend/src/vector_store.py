import os
import json
import logging
from typing import List, Dict, Any, Optional
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from dotenv import load_dotenv

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vector_store.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        """Khởi tạo vector store"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Lấy COHERE_API_KEY từ biến môi trường
            self.cohere_api_key = os.getenv("COHERE_API_KEY")
            if self.cohere_api_key:
                logger.info("Cohere API key found in environment variables.")
            else:
                logger.warning("No Cohere API key found in environment variables.")
                self.cohere_api_key = ""
            
            # Tạo embeddings
            self.embeddings = CohereEmbeddings(
                cohere_api_key=self.cohere_api_key,
                model="embed-multilingual-v3.0",
                user_agent="langchain",
            )
                
            # Đường dẫn đến thư mục và file lưu vector store
            self.index_folder = "index_data"
            self.index_name = "index"
            self.index_file = os.path.join(self.index_folder, f"{self.index_name}.faiss")
            
            # Kiểm tra và tải vector store nếu tồn tại
            try:
                if os.path.exists(self.index_file):
                    logger.info(f"Tải vector store từ file {self.index_file}")
                    self.vectorstore = FAISS.load_local(
                        self.index_folder, 
                        self.embeddings, 
                        self.index_name,
                        allow_dangerous_deserialization=True
                    )
                    logger.info("Vector store đã được khởi tạo thành công")
                else:
                    logger.warning(f"File index {self.index_file} không tồn tại, vector store sẽ được khởi tạo")
                    self.initialize_vector_store()
            except Exception as e:
                logger.warning(f"Không thể tải vector store từ file: {str(e)}")
                # Khởi tạo vector store mới
                self.initialize_vector_store()
                
        except Exception as e:
            logger.error(f"Lỗi khởi tạo VectorStore: {str(e)}")
            self.vectorstore = None

    def initialize_vector_store(self, courses_file="data/courses.json"):
        """
        Khởi tạo vector store từ file khóa học
        
        Args:
            courses_file: Đường dẫn đến file JSON chứa thông tin khóa học
        """
        try:
            # Load khóa học từ file
            with open(courses_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                courses = data['courses']
            
            # Tạo text representations cho các khóa học
            texts = []
            metadatas = []
            
            for course in courses:
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
            
            # Tạo documents
            documents = [
                Document(page_content=text, metadata=metadata)
                for text, metadata in zip(texts, metadatas)
            ]
            
            # Nếu đã có vector store, thì xóa bỏ và tạo mới
            if os.path.exists(self.index_file):
                os.remove(self.index_file)
                pkl_file = os.path.join(self.index_folder, f"{self.index_name}.pkl")
                if os.path.exists(pkl_file):
                    os.remove(pkl_file)
            
            # Khởi tạo embeddings model
            embeddings = CohereEmbeddings(
                cohere_api_key=os.getenv("COHERE_API_KEY"),
                model="embed-multilingual-v3.0",
                user_agent="learning-path-rag"
            )
            
            # Tạo vector store
            self.vectorstore = FAISS.from_documents(documents, embeddings)
            
            # Lưu vector store ra file
            if not os.path.exists(self.index_folder):
                os.makedirs(self.index_folder)
                
            self.vectorstore.save_local(self.index_folder, self.index_name)
            
            logger.info("Đã tạo vector store thành công")
            
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo vector store: {str(e)}")
            raise

    def search_courses(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Tìm kiếm khóa học phù hợp dựa trên câu truy vấn"""
        try:
            if not self.vectorstore:
                logger.warning("Vector store chưa được khởi tạo, thử khởi tạo lại")
                self.initialize_vector_store()
                
            if not self.vectorstore:
                raise ValueError("Vector store chưa được khởi tạo và không thể khởi tạo tự động")
            
            # Tìm kiếm các document phù hợp
            logger.info(f"Thực hiện similarity_search_with_score cho query: '{query}'")
            docs = self.vectorstore.similarity_search_with_score(query, k=n_results)
            logger.info(f"Kết quả tìm kiếm (docs): {docs}") # Log kết quả trả về
            
            # Format kết quả
            results = []
            for doc, score in docs:
                metadata = doc.metadata
                results.append({
                    "title": metadata.get("title", "Unknown"),
                    "level": metadata.get("level", "Unknown"),
                    "duration": metadata.get("duration", 0),
                    "topics": metadata.get("topics", []),
                    "relevance_score": 1 - score  # Convert distance to similarity
                })
            
            return results
            
        except Exception as e:
            # logger.error(f"Lỗi tìm kiếm khóa học: {str(e)}") # Dòng cũ
            logger.exception(f"Lỗi tìm kiếm khóa học:") # Log đầy đủ traceback
            return [] 