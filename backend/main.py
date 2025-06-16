import os
import sys
import time
import platform
import uvicorn
from flask import Flask
from datetime import datetime

# Import các module cần thiết
from init_db import init_db
from unified_api import app as flask_app
from swagger_ui import setup_swagger

# In màu cho terminal
def print_colored(text, color):
    """Print colored text based on platform"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'end': '\033[0m'
    }
    
    if platform.system() == "Windows":
        # Check if running in a terminal that supports ANSI colors
        if os.environ.get('TERM') or 'WT_SESSION' in os.environ:
            print(f"{colors[color]}{text}{colors['end']}")
        else:
            print(text)
    else:
        print(f"{colors[color]}{text}{colors['end']}")

def main():
    """Main function to initialize database and run the API server"""
    print_colored("=== RAG Learning Path API Service ===", "cyan")
    print_colored(f"Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "blue")
    print("")
    
    # Bước 1: Khởi tạo cơ sở dữ liệu
    print_colored("Bước 1: Đang khởi tạo cơ sở dữ liệu...", "yellow")
    success = init_db()
    
    if not success:
        print_colored("Lỗi khởi tạo cơ sở dữ liệu.", "red")
        input("Nhấn Enter để thoát...")
        return
    
    print_colored("✓ Cơ sở dữ liệu đã được khởi tạo thành công.", "green")
    print("")
    
    # Bước 2: Thiết lập Swagger UI
    print_colored("Bước 2: Đang cài đặt Swagger UI...", "yellow")
    try:
        setup_swagger(flask_app)
        print_colored("✓ Swagger UI đã được cài đặt thành công.", "green")
        print("")
    except Exception as e:
        print_colored(f"Cảnh báo: Không thể cài đặt Swagger UI: {str(e)}", "yellow")
        print("")
    
    # Bước 3: Khởi động API server
    print_colored("Bước 3: Đang khởi động API server...", "yellow")
    
    print_colored("✓ API server đang chạy tại địa chỉ:", "green")
    print_colored("   http://localhost:5000", "magenta")
    print_colored("✓ Swagger UI có thể truy cập tại:", "green")
    print_colored("   http://localhost:5000/api/docs", "magenta")
    print("")
    print_colored("Thông tin đăng nhập:", "cyan")
    print_colored("   Username: admin", "white")
    print_colored("   Password: admin123", "white")
    print("")
    print_colored("Nhấn Ctrl+C để dừng server.", "yellow")
    
    try:
        # On Windows, set the window title
        if platform.system() == "Windows":
            os.system('title RAG Learning Path API Server')
        
        # Chạy Flask app
        flask_app.run(debug=True, port=5000, host='0.0.0.0')
        
    except KeyboardInterrupt:
        print("")
        print_colored("API server đã dừng bởi người dùng.", "yellow")
    except Exception as e:
        print_colored(f"Lỗi khi chạy API server: {str(e)}", "red")

if __name__ == "__main__":
    main() 