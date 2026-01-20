
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(500), default='default_avatar.png')
    theme = db.Column(db.String(20), default='light')
    accent_color = db.Column(db.String(20), default='#3b82f6')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- RELATIONSHIPS ---
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    
    sent_friend_requests = db.relationship('FriendRequest', 
                                           foreign_keys='FriendRequest.sender_id',
                                           backref='sender', lazy=True)
    received_friend_requests = db.relationship('FriendRequest',
                                               foreign_keys='FriendRequest.receiver_id',
                                               backref='receiver', lazy=True)
                                               
    # --- ĐÃ XÓA QUAN HỆ MESSAGE GÂY LỖI ---
    # Vì Message bây giờ liên kết qua Conversation, không còn receiver_id trực tiếp
    # Nếu cần lấy tin nhắn đã gửi, ta sẽ query trực tiếp từ bảng Message

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'theme': self.theme,
            'accent_color': self.accent_color,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))