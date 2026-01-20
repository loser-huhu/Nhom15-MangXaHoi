import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class FileUploadService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in FileUploadService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_image(file, folder_name):
        if not file or file.filename == '':
            return None
        
        if FileUploadService.allowed_file(file.filename):
            # Tạo tên file độc nhất để tránh trùng
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Lấy đường dẫn từ app config
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)
            
            # Đảm bảo thư mục tồn tại
            os.makedirs(upload_path, exist_ok=True)
            
            # Lưu file
            try:
                file.save(os.path.join(upload_path, unique_filename))
                return unique_filename
            except Exception as e:
                print(f"Save Error: {e}")
                return None
        return None

    @staticmethod
    def save_background(file):
        """Lưu ảnh nền chat"""
        return FileUploadService.save_image(file, 'backgrounds')