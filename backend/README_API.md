# API Hệ Thống Lộ Trình Học Tập

Hệ thống API cho ứng dụng tạo lộ trình học tập cá nhân hóa với khả năng theo dõi tiến độ

## Tính Năng Mới

Phiên bản mới của API bổ sung các tính năng:

1. **Xác thực người dùng**: Đăng ký, đăng nhập, đăng xuất
2. **Quản lý lộ trình học tập**: Lưu và lấy thông tin lộ trình học tập
3. **Theo dõi tiến độ học tập**: Đánh dấu nhiệm vụ hoàn thành, xem thống kê học tập

## Cài Đặt và Chạy

1. **Tải Mã Nguồn**

```bash
git clone <repository-url>
cd RAG
```

2. **Cài Đặt Thư Viện**

```bash
pip install -r requirements.txt
```

3. **Cấu Hình API Key**

Tạo file `.env` với nội dung:

```
COHERE_API_KEY=your_cohere_api_key
GOOGLE_API_KEY=your_google_api_key
```

4. **Chạy Server**

```bash
python -m src.api
```

Server sẽ chạy tại `http://localhost:5000`

## API Endpoints

### Xác Thực Người Dùng

#### Đăng ký tài khoản

```
POST /api/auth/register
```

**Body:**
```json
{
  "username": "example_user",
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com",
    "created_at": "2023-05-20T15:30:45.123456"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Đăng nhập

```
POST /api/auth/login
```

**Body:**
```json
{
  "username": "example_user",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com",
    "created_at": "2023-05-20T15:30:45.123456"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Đăng xuất

```
POST /api/auth/logout
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Đăng xuất thành công"
}
```

#### Lấy thông tin người dùng hiện tại

```
GET /api/auth/me
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com",
    "created_at": "2023-05-20T15:30:45.123456"
  }
}
```

### Lộ Trình Học Tập

#### Tạo lộ trình học tập

```
POST /api/learning-path
```

**Body:**
```json
{
  "field": "Python programming",
  "level": "Beginner",
  "duration": 3,
  "daily_hours": 2,
  "interests": ["Web Development", "Data Science"]
}
```

**Response:**
```json
{
  "learning_path": {
    "courses": [...],
    "daily_plan": [...],
    "phases": [...],
    "field": "Python programming",
    "level": "Beginner",
    "duration": 3,
    "daily_hours": 2,
    "interests": ["Web Development", "Data Science"],
    ...
  }
}
```

#### Lưu lộ trình học tập vào cơ sở dữ liệu

```
POST /api/progress/learning-paths/<path_id>/save
```

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
  "learning_path": {
    // Dữ liệu lộ trình học tập từ RAG API
  }
}
```

**Response:**
```json
{
  "message": "Lộ trình học tập đã được lưu thành công",
  "path_id": 1
}
```

### Quản Lý Tiến Độ

#### Lấy danh sách lộ trình của người dùng

```
GET /api/progress/learning-paths
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "learning_paths": [
    {
      "id": 1,
      "field": "Python programming",
      "level": "Beginner",
      "duration": 3,
      "daily_hours": 2,
      "total_hours": 180,
      "created_at": "2023-05-20T15:30:45.123456",
      "progress": {
        "total_tasks": 90,
        "completed_tasks": 30,
        "completion_percentage": 33,
        "skills": [...]
      }
    }
  ]
}
```

#### Lấy chi tiết lộ trình học tập

```
GET /api/progress/learning-paths/<path_id>
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "learning_path": {
    "id": 1,
    "field": "Python programming",
    "level": "Beginner",
    "duration": 3,
    "daily_hours": 2,
    "total_hours": 180,
    "created_at": "2023-05-20T15:30:45.123456",
    "tasks_by_phase": {
      "Phase 1: Basics": [
        {
          "id": 1,
          "title": "Cài đặt Python",
          "description": "Cài đặt Python và môi trường lập trình",
          "completed": true,
          "date": "2023-05-21T00:00:00"
        },
        ...
      ],
      ...
    },
    "progress": [...]
  }
}
```

#### Chuyển trạng thái hoàn thành nhiệm vụ

```
POST /api/progress/tasks/<task_id>/toggle
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "task": {
    "id": 1,
    "completed": true
  },
  "progress": {
    "skill_name": "Phase 1: Basics",
    "progress_percentage": 50
  }
}
```

#### Thêm ghi chú cho nhiệm vụ

```
POST /api/progress/tasks/<task_id>/notes
```

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
  "notes": "Ghi chú về thực hiện nhiệm vụ này"
}
```

**Response:**
```json
{
  "task": {
    "id": 1,
    "description": "Cài đặt Python và môi trường lập trình\n\nGhi chú: Ghi chú về thực hiện nhiệm vụ này"
  }
}
```

#### Xem thống kê học tập theo tuần

```
GET /api/progress/stats/weekly
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "daily_stats": [
    {
      "date": "2023-05-14",
      "day_of_week": "Sunday",
      "completed_tasks": 5
    },
    ...
  ],
  "overall_stats": {
    "total_paths": 1,
    "total_tasks": 90,
    "completed_tasks": 30,
    "completion_percentage": 33,
    "current_streak": 5
  }
}
```

## Kiểm Thử API

Để kiểm thử các API, bạn có thể sử dụng script kiểm thử tự động:

```bash
python test_auth_progress.py
```

Script này sẽ thực hiện quy trình đầy đủ bao gồm:
- Đăng ký tài khoản mới
- Đăng nhập
- Tạo lộ trình học tập
- Lưu lộ trình vào cơ sở dữ liệu
- Lấy danh sách lộ trình
- Lấy chi tiết lộ trình
- Chuyển trạng thái hoàn thành nhiệm vụ
- Xem thống kê học tập
- Đăng xuất

## Tài Liệu Tham Khảo

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Cohere API](https://cohere.com/)
- [Google Gemini API](https://ai.google.dev/) 