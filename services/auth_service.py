from models.user import User
from extensions import db
from flask_login import login_user
from datetime import datetime

class AuthService:
    @staticmethod
    def authenticate(phone_number, password):
        """Xác thực người dùng bằng số điện thoại và mật khẩu"""
        try:
            user = User.query.filter_by(phone_number=phone_number).first()
            
            if user and user.check_password(password):
                # Cập nhật thời gian hoạt động cuối cùng
                try:
                    if hasattr(user, 'update_last_seen'):
                        user.update_last_seen()
                    else:
                        # Fallback nếu không có phương thức
                        user.last_seen = datetime.utcnow()
                        db.session.commit()
                except Exception as e:
                    print(f"Warning: Could not update last_seen: {e}")
                
                login_user(user, remember=True)
                return user
            
            return None
        except Exception as e:
            print(f"AuthService authenticate error: {e}")
            return None
    
    @staticmethod
    def register(phone_number, password, name=""):
        """Đăng ký người dùng mới"""
        try:
            # Kiểm tra độ mạnh mật khẩu
            is_valid, error_message = User.validate_password_strength(password)
            if not is_valid:
                raise ValueError(error_message)
            
            # Kiểm tra xem số điện thoại đã tồn tại chưa
            if User.query.filter_by(phone_number=phone_number).first():
                return None
            
            # Tạo người dùng mới
            user = User(phone_number=phone_number, name=name if name else phone_number)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user, remember=True)
            return user
        except Exception as e:
            db.session.rollback()
            print(f"AuthService register error: {e}")
            return None
    
    @staticmethod
    def is_phone_registered(phone_number):
        """Kiểm tra xem số điện thoại đã được đăng ký chưa"""
        try:
            return User.query.filter_by(phone_number=phone_number).first() is not None
        except Exception as e:
            print(f"AuthService is_phone_registered error: {e}")
            return False