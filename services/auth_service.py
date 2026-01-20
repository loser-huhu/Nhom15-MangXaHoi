from models.user import User
from app import db
from flask_login import login_user

class AuthService:
    @staticmethod
    def authenticate(phone_number, password):
        """Authenticate user by phone number and password"""
        user = User.query.filter_by(phone_number=phone_number).first()
        
        if user and user.check_password(password):
            user.update_last_seen()
            login_user(user, remember=True)
            return user
        
        return None
    
    @staticmethod
    def register(phone_number, password, name=""):
        """Register new user"""
        # Check if user exists
        if User.query.filter_by(phone_number=phone_number).first():
            return None
        
        # Create new user
        user = User(phone_number=phone_number, name=name)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user, remember=True)
        return user
    
    @staticmethod
    def is_phone_registered(phone_number):
        """Check if phone number is already registered"""
        return User.query.filter_by(phone_number=phone_number).first() is not None