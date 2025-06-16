# API Tích Hợp Hệ Thống Lộ Trình Học Tập

Hệ thống API tích hợp cho ứng dụng tạo lộ trình học tập cá nhân hóa với xác thực và theo dõi tiến độ.

## Tính Năng

API tích hợp bao gồm đầy đủ các tính năng:

1. **Xác thực người dùng**: Đăng ký, đăng nhập, đăng xuất trong một API duy nhất
2. **Tạo lộ trình học tập**: Sử dụng RAG để tạo lộ trình học tập cá nhân hóa
3. **Theo dõi tiến độ học tập**: Lưu lộ trình, đánh dấu nhiệm vụ hoàn thành, xem thống kê học tập

## Cài Đặt và Chạy

1. **Cài Đặt Thư Viện**

```bash
pip install -r requirements.txt
```

2. **Cấu Hình API Key**

Tạo file `.env` với nội dung:

```
COHERE_API_KEY=your_cohere_api_key
GOOGLE_API_KEY=your_google_api_key
```

3. **Chạy Server Tích Hợp**

Sử dụng script tự động:

```bash
run_unified_api.bat
```

Hoặc chạy thủ công:

```bash
# Khởi tạo database và tạo tài khoản admin
python init_db.py

# Khởi động server API tích hợp
python unified_api.py
```

Server sẽ chạy tại `http://localhost:5000` và có thể truy cập từ bất kỳ thiết bị nào trong mạng LAN.

## API Endpoints

### Xác Thực Người Dùng

| Phương thức | Endpoint | Mô tả |
|-------------|----------|-------|
| POST | `/api/auth/register` | Đăng ký tài khoản mới |
| POST | `/api/auth/login` | Đăng nhập và lấy token |
| POST | `/api/auth/logout` | Đăng xuất và hủy token |
| GET | `/api/auth/me` | Lấy thông tin người dùng hiện tại |

### Lộ Trình Học Tập

| Phương thức | Endpoint | Mô tả |
|-------------|----------|-------|
| POST | `/api/learning-path` | Tạo lộ trình học tập mới |

### Quản Lý Tiến Độ

| Phương thức | Endpoint | Mô tả |
|-------------|----------|-------|
| GET | `/api/progress/learning-paths` | Lấy danh sách lộ trình của người dùng |
| GET | `/api/progress/learning-paths/<path_id>` | Xem chi tiết một lộ trình cụ thể |
| POST | `/api/progress/learning-paths/<path_id>/save` | Lưu lộ trình học tập vào cơ sở dữ liệu |
| POST | `/api/progress/tasks/<task_id>/toggle` | Đánh dấu hoàn thành/chưa hoàn thành |
| POST | `/api/progress/tasks/<task_id>/notes` | Thêm ghi chú cho nhiệm vụ |
| GET | `/api/progress/stats/weekly` | Xem thống kê học tập theo tuần |

## Tích Hợp Frontend

### Cấu Hình API URL

```javascript
// Trong file frontend-ai/src/services/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";
```

### Ví Dụ Đăng Ký Và Đăng Nhập

```javascript
// Đăng ký
const register = async (data) => {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Đăng ký thất bại');
  }
  
  return response.json();
};

// Đăng nhập
const login = async (username, password) => {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password })
  });
  
  if (!response.ok) {
    throw new Error('Đăng nhập thất bại');
  }
  
  return response.json();
};
```

### Gọi API Với Token

```javascript
// Gửi request với token xác thực
const authRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('token');
  
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
  };
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      // Token hết hạn, chuyển về trang login
      window.location.href = '/login';
      return;
    }
    throw new Error('API request failed');
  }
  
  return response.json();
};

// Ví dụ: Lấy danh sách lộ trình
const getLearningPaths = async () => {
  return authRequest('/progress/learning-paths');
};
```

## Tài Khoản Mặc Định

Khi chạy `init_db.py`, một tài khoản admin sẽ được tạo tự động:

- **Username**: admin
- **Password**: admin123

Bạn có thể sử dụng tài khoản này để đăng nhập và thử nghiệm API. 