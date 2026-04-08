# 📚 Telegram Flashcard Bot

Bot học từ vựng thông minh tích hợp trên Telegram, giúp bạn lưu trữ, tra cứu và ôn luyện tiếng Anh (đặc biệt là IELTS) một cách hiệu quả và tự động. Bot sử dụng chính Telegram Chat làm "cơ sở dữ liệu" cá nhân của bạn.

---

## ✨ Tính năng chính

-   **🧠 Học qua Flashcard**: Tự động tạo câu hỏi trắc nghiệm (MCQ) từ kho từ vựng của bạn.
-   **🚀 IELTS Upskill**: Sử dụng AI (Google Gemini 1.5 Flash) để tạo các câu hỏi luyện tập trình độ IELTS 7.0+.
-   **🔍 Tra từ điển thông minh**: Tích hợp tra cứu trực tiếp từ **Cambridge Dictionary** chỉ bằng một câu lệnh.
-   **💾 Lưu trữ tức thì**: Thêm từ vựng mới vào kho luyện tập cá nhân chỉ với một lần bấm nút từ kết quả tìm kiếm.
-   **🛡️ Quản lý theo nhóm**: Hỗ trợ phân quyền lệnh theo Chat ID (ví dụ: chỉ hiện `/help` trong nhóm quản trị).
-   **🐳 Sẵn sàng cho Docker**: Cài đặt và vận hành cực dễ dàng qua Docker.

---

## 🛠️ Cài đặt & Cấu hình

### 1. Yêu cầu hệ thống
-   Python 3.10+
-   API ID & API Hash từ [my.telegram.org](https://my.telegram.org)
-   Gemini API Key từ [Google AI Studio](https://aistudio.google.com/)

### 2. Biến môi trường (`.env`)
Tạo file `.env` tại thư mục gốc và điền các thông tin sau:
```env
TELETHON_API_ID=your_api_id
TELETHON_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Cách chạy bot

#### Cách 1: Chạy trực tiếp (Local)
```bash
pip install -r requirements.txt
python main.py
```

#### Cách 2: Chạy bằng Docker (Khuyên dùng)
```bash
docker-compose up --build -d
```
*Lưu ý: Docker đã được cấu hình Volume để giữ lại file session đăng nhập, bạn không cần login lại khi khởi động lại container.*

---

## 🎮 Hướng dẫn sử dụng

| Lệnh | Mô tả |
| :--- | :--- |
| `/start` | Bắt đầu học, hiển thị menu trắc nghiệm và từ vựng |
| `/search <từ>` | Tra nghĩa từ điển Cambridge và tùy chọn lưu vào kho |
| `/help` | Xem hướng dẫn sử dụng chi tiết |

---

## 🏗️ Kiến trúc dự án
-   **`core/`**: Xử lý logic nghiệp vụ chính của bot.
-   **`engine/`**: Quản lý kết nối Telethon và xử lý dữ liệu từ vựng.
-   **`utils/`**: Các công cụ bổ trợ (AI Gemini, Scraper từ điển, Constants).

---

## 🤝 Đóng góp
Nếu bạn có ý tưởng mới hoặc phát hiện lỗi, hãy tạo **Issue** hoặc gửi **Pull Request**. Mọi đóng góp đều được chào đón!

---
*Phát triển bởi [Antigravity AI Assistant]*
