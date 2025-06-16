# Thiết lập encoding cho PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Hiển thị thông báo
Write-Host "Khởi động API tạo lộ trình học tập..." -ForegroundColor Green
Write-Host "Truy cập API tại http://localhost:5000"
Write-Host ""

# Kiểm tra và cài đặt thư viện Flask nếu cần
try {
    python -c "import flask"
    Write-Host "Flask đã được cài đặt." -ForegroundColor Green
}
catch {
    Write-Host "Đang cài đặt Flask..." -ForegroundColor Yellow
    python -m pip install flask
}

# Kiểm tra Google API key
$env_file = ".env"
if (Test-Path $env_file) {
    $env_content = Get-Content $env_file -Encoding UTF8 -Raw
    if ($env_content -notmatch "GOOGLE_API_KEY=AI") {
        Write-Host "CẢNH BÁO: Không tìm thấy Google API key hợp lệ trong file .env" -ForegroundColor Yellow
        Write-Host "API sẽ sử dụng lộ trình dự phòng thay vì gọi Gemini API" -ForegroundColor Yellow
    }
    else {
        Write-Host "Google API key đã được cấu hình." -ForegroundColor Green
    }
}
else {
    Write-Host "Không tìm thấy file .env" -ForegroundColor Red
}

# Chạy API
Write-Host "Đang khởi động API..." -ForegroundColor Green
python direct_api.py 