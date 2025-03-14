import os
from datetime import timedelta

# Cấu hình cơ bản
SECRET_KEY = 'your-secret-key-change-in-production'
SQLALCHEMY_DATABASE_URI = 'sqlite:///task_manager.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Cấu hình cho session
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Đường dẫn tải lên
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)