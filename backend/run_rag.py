import sys
import os

# Thêm thư mục gốc vào sys.path để có thể import các module từ src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import hàm main từ rag_system
from src.rag_system import main

if __name__ == "__main__":
    main()
