import os
import json
import time
import sys
import io
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from src.rag_system import LearningPathRAG
from src.auth_api import auth_api
from src.progress_api import progress_api

# Cấu hình encoding cho console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Tạo Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(auth_api)
app.register_blueprint(progress_api)

# Load biến môi trường
load_dotenv()

# Thiết lập GOOGLE_API_KEY
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
    # Sử dụng Google API key cố định để test
    print("CẢNH BÁO: Không tìm thấy GOOGLE_API_KEY hợp lệ. Vui lòng đặt API key trong file .env")
    
    # Nếu không có key thật, hãy sử dụng key test
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
        if "GOOGLE_API_KEY=" not in content or "GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE" in content:
            with open(".env", "a", encoding="utf-8") as f:
                f.write("\n# Thêm API key thật của bạn vào đây\nGOOGLE_API_KEY=AIzaSyDaRTFCx2MrGqaqVE_l0AB8TX-iu1Xu0V4\n")
            print("Đã thêm API key test vào file .env. Vui lòng thay thế bằng API key thật của bạn.")
            os.environ["GOOGLE_API_KEY"] = "AIzaSyDaRTFCx2MrGqaqVE_l0AB8TX-iu1Xu0V4"
    else:
        with open(".env", "w", encoding="utf-8") as f:
            f.write("COHERE_API_KEY=" + os.getenv("COHERE_API_KEY", "") + "\n")
            f.write("GOOGLE_API_KEY=AIzaSyDaRTFCx2MrGqaqVE_l0AB8TX-iu1Xu0V4\n")
        print("Đã tạo file .env với API key test. Vui lòng thay thế bằng API key thật của bạn.")
        os.environ["GOOGLE_API_KEY"] = "AIzaSyDaRTFCx2MrGqaqVE_l0AB8TX-iu1Xu0V4"
else:
    print(f"Đã tìm thấy GOOGLE_API_KEY: {GOOGLE_API_KEY[:5]}...")

# Khởi tạo RAG system
try:
    rag_system = LearningPathRAG(cohere_api_key=os.getenv("COHERE_API_KEY"))
    print("Khởi tạo RAG system thành công!")
except Exception as e:
    print(f"Lỗi khởi tạo RAG system: {str(e)}")
    rag_system = None

@app.route('/api/learning-path', methods=['POST'])
def create_learning_path():
    """API endpoint để tạo lộ trình học tập"""
    try:
        # Kiểm tra RAG system
        if rag_system is None:
            return jsonify({"error": "RAG system chưa được khởi tạo"}), 500
        
        # Lấy dữ liệu từ request
        data = request.json
        username = request.args.get('username', 'anonymous')
        
        # Kiểm tra dữ liệu
        required_fields = ['field', 'level', 'duration', 'daily_hours', 'interests']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Thiếu trường {field}"}), 400
        
        print(f"Nhận được yêu cầu tạo lộ trình học tập từ {username}: {data['field']}, {data['level']}")
        
        # Gọi RAG system để tạo lộ trình
        start_time = time.time()
        learning_path = rag_system.create_learning_path(
            field=data['field'],
            level=data['level'],
            duration=data['duration'],
            daily_hours=data['daily_hours'],
            interests=data['interests']
        )
        elapsed_time = time.time() - start_time
        print(f"Tạo lộ trình học tập hoàn tất trong {elapsed_time:.2f} giây")
        
        # Lưu kết quả vào file để debug
        try:
            save_path = f"learning_path_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(learning_path, f, ensure_ascii=False, indent=2)
            print(f"Đã lưu lộ trình học tập vào file {save_path}")
        except Exception as e:
            print(f"Không thể lưu lộ trình học tập: {str(e)}")
        
        # Kiểm tra xem có phải là fallback không
        if "learning_path" in learning_path and learning_path["learning_path"].get("is_fallback", False):
            print(f"Cảnh báo: Sử dụng lộ trình dự phòng - {learning_path['learning_path'].get('fallback_reason', 'Unknown')}")
        
        return jsonify(learning_path), 200
        
    except Exception as e:
        print(f"Lỗi xử lý request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """API endpoint để kiểm tra trạng thái"""
    return jsonify({
        "status": "ok", 
        "rag_system": rag_system is not None,
        "version": "1.1.0",
        "features": ["authentication", "learning_path", "progress_tracking"]
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Trang chủ"""
    return """
    <html>
        <head>
            <title>API Tạo Lộ Trình Học Tập</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #2c3e50; }
                h2 { color: #3498db; margin-top: 30px; }
                code { background: #f8f8f8; padding: 2px 4px; border-radius: 4px; }
                pre { background: #f8f8f8; padding: 10px; border-radius: 4px; overflow-x: auto; }
                button { background: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
                button:hover { background: #2980b9; }
                #result { white-space: pre-wrap; background: #f8f8f8; padding: 10px; border-radius: 4px; display: none; }
                .endpoint { border-left: 4px solid #3498db; padding-left: 15px; margin-bottom: 20px; }
                .new { background-color: #e8f7f0; border-radius: 4px; padding: 2px 5px; color: #27ae60; font-size: 12px; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>API Tạo Lộ Trình Học Tập</h1>
            <p>Hệ thống API cung cấp các tính năng tạo lộ trình học tập cá nhân hóa, quản lý tài khoản và theo dõi tiến độ học tập.</p>
            
            <h2>1. Lộ Trình Học Tập</h2>
            <div class="endpoint">
                <p><code>POST /api/learning-path</code> - Tạo lộ trình học tập mới</p>
                <pre>
{
  "field": "Python programming",
  "level": "Beginner",
  "duration": 3,
  "daily_hours": 2,
  "interests": ["Web Development", "Data Science"]
}
                </pre>
            </div>
            
            <h2>2. Xác Thực <span class="new">Mới</span></h2>
            <div class="endpoint">
                <p><code>POST /api/auth/register</code> - Đăng ký tài khoản mới</p>
                <pre>
{
  "username": "example_user",
  "email": "user@example.com",
  "password": "secure_password"
}
                </pre>
            </div>
            <div class="endpoint">
                <p><code>POST /api/auth/login</code> - Đăng nhập</p>
                <pre>
{
  "username": "example_user",
  "password": "secure_password"
}
                </pre>
            </div>
            <div class="endpoint">
                <p><code>POST /api/auth/logout</code> - Đăng xuất</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            
            <h2>3. Theo Dõi Tiến Độ <span class="new">Mới</span></h2>
            <div class="endpoint">
                <p><code>GET /api/progress/learning-paths</code> - Lấy danh sách lộ trình của người dùng</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            <div class="endpoint">
                <p><code>GET /api/progress/learning-paths/{path_id}</code> - Xem chi tiết một lộ trình cụ thể</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            <div class="endpoint">
                <p><code>POST /api/progress/tasks/{task_id}/toggle</code> - Đánh dấu hoàn thành/chưa hoàn thành</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            <div class="endpoint">
                <p><code>GET /api/progress/stats/weekly</code> - Xem thống kê học tập theo tuần</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            
            <h2>Test nhanh:</h2>
            <button onclick="testAPI()">Tạo lộ trình Python cho người mới</button>
            <div id="loading" style="display:none; margin-top: 10px;">Đang xử lý, vui lòng đợi...</div>
            <pre id="result"></pre>
            
            <script>
                function testAPI() {
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('result').style.display = 'none';
                    
                    fetch('/api/learning-path?username=test_user', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            field: "Python programming",
                            level: "Beginner",
                            duration: 3,
                            daily_hours: 2,
                            interests: ["Web Development", "Data Science"]
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                    })
                    .catch(error => {
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('result').textContent = 'Error: ' + error;
                    });
                }
            </script>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("Khởi động API service...")
    print(f"GOOGLE_API_KEY: {os.environ.get('GOOGLE_API_KEY', 'NOT_SET')[:5]}...")
    print(f"COHERE_API_KEY: {os.environ.get('COHERE_API_KEY', 'NOT_SET')[:5]}...")
    print("Có thể truy cập API tại: http://localhost:5000")
    print("Các tính năng mới: Xác thực người dùng, Theo dõi tiến độ")
    app.run(debug=True, port=5000) 