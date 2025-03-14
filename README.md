# Quản Lý Công Việc (Task Management App)

## 1. Thông Tin Sinh Viên
- **Nguyễn Hoàng Ái Linh** - MSSV: 22634681


## 2. Mô Tả Dự Án
Ứng dụng Quản Lý Công Việc cho phép quản lý danh sách công việc (task), tình trạng hoàn thành (status), thời gian tạo (created), thời gian hoàn thành (finished) với hai loại tài khoản: **Admin** và **User**.

### Tính năng chính:
- 📝 Đăng ký và đăng nhập
- ✅ Theo dõi trạng thái công việc**: Đã hoàn thành, Đang thực hiện, Trễ hạn
- 📅 Thống kê mô tả công việc
- 🚀 Quản lý phân loại công việc
- 🖼  Upload avatar cho người dùng
- 🔔 Hiển thị cảnh báo số công việc trễ hạn (Option 1) 
- 🎨 Giao diện: Layout **Single Column** 

## 3. Hướng Dẫn Cài Đặt & Chạy Dự Án

### 3.1 Yêu Cầu Hệ Thống
- Python >= 3.8
- Flask Framework
- SQLite
- Bootstrap/TailwindCSS (cho frontend)

### 3.2 Cài Đặt Dự Án
#### 📥 Clone repository
```bash
git clone https://github.com/yourusername/ptud-gk-de-2.git
cd ptud-gk-de-2
```

#### 🛠 Tạo môi trường ảo và kích hoạt
```bash
python -m venv venv  # Tạo môi trường ảo
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

#### 📦 Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

#### 📁 Thư mục `libs`
```bash
Thư mục `libs` chứa các thư viện cần thiết cho dự án, bao gồm các dependency bên ngoài như Flask, SQLAlchemy, và các thư viện hỗ trợ khác.  
Nó giúp đảm bảo mã nguồn hoạt động mà không cần cài đặt các thư viện từ internet mỗi lần chạy dự án.
```

#### 🚀 Chạy ứng dụng Flask
```bash
python app.py
```
