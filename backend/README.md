# Hệ thống Đề xuất Khóa học Thông minh (Hybrid RAG)

Hệ thống này sử dụng mô hình lai (Hybrid RAG) kết hợp giữa Cohere và Google Gemini AI:
- **R**etrieval (Truy xuất): Sử dụng Cohere cho vector embeddings và tìm kiếm ngữ nghĩa
- **A**ugmentation (Tăng cường): Kết hợp dữ liệu truy xuất với prompt
- **G**eneration (Sinh): Sử dụng Google Gemini AI để tạo ra đề xuất và lộ trình học tập

## Cài đặt

1. Clone repository này
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

3. Tạo file `.env` và thêm cả hai API key:
```
GOOGLE_API_KEY=your_google_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
```

## Cấu hình API Keys

### Cohere API Key (cho phần Retrieval)
1. Đăng ký và tạo API key tại [Cohere Dashboard](https://dashboard.cohere.com/api-keys)
2. Sao chép API key và dán vào file `.env` với tên `COHERE_API_KEY`

### Google API Key (cho phần Generation)
1. Đăng ký và tạo API key tại [Google AI Studio](https://ai.google.dev/)
2. Đảm bảo bạn đã bật (enable) Gemini API trong dự án Google Cloud của bạn
3. Sao chép API key và dán vào file `.env` với tên `GOOGLE_API_KEY`

## Kiểm tra API Keys

Trước khi chạy ứng dụng chính, bạn nên kiểm tra cả hai API key để đảm bảo chúng hoạt động chính xác:

```bash
python test_api_keys.py
```

Nếu kiểm tra thành công, bạn sẽ thấy thông báo "All tests passed! Your API keys are valid and working correctly."

## Các ví dụ sử dụng API Gemini

### Sử dụng trong Python:

```python
# Sử dụng thư viện google.generativeai
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content("Say hello in Vietnamese")
print(response.text)

# Hoặc sử dụng google.genai (Client API)
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
response = client.models.generate_content(
    model="gemini-2.0-flash", 
    contents="Explain how AI works in a few words"
)
print(response.text)
```

### Sử dụng trong Node.js:

```javascript
import dotenv from 'dotenv';
import fetch from 'node-fetch';

dotenv.config();

const apiKey = process.env.API_KEY;

async function main() {
  const generationConfig = {
    temperature: 1,
    topP: 0.95,
    topK: 40,
    maxOutputTokens: 8192,
    responseMimeType: 'text/plain',
  };

  const data = {
    generationConfig,
    contents: [
      {
        role: 'user',
        parts: [
          { text: 'Xin chào' },
        ],
      },
    ],
  };

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  const responseData = await response.json();
  console.log("Kết quả trả về từ Gemini:", responseData.candidates[0].content);
}

main();
```

## Chạy ứng dụng

1. Khởi động server:
```bash
python main.py
```

2. Truy cập API docs tại: http://localhost:8000/docs

## API Endpoints
http://localhost:8000/api/...

## Lưu ý kỹ thuật

- **Phần Retrieval**: Sử dụng Cohere với mô hình embeddings `embed-multilingual-light-v3.0`
- **Phần Generation**: Sử dụng Google Gemini với mô hình `gemini-2.0-flash` và nhiệt độ 0.7
- Mỗi API key cần có đủ credits để sử dụng