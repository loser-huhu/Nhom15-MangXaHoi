# from datetime import datetime
# from app import db

# class FriendRequest(db.Model):
#     __tablename__ = 'friend_requests'
    
#     id = db.Column(db.Integer, primary_key=True)
#     sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     status = db.Column(db.Enum('pending', 'accepted', 'rejected', name='friend_status'),
#                       default='pending')
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
#     __table_args__ = (db.UniqueConstraint('sender_id', 'receiver_id', name='unique_friend_request'),)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'sender_id': self.sender_id,
#             'receiver_id': self.receiver_id,
#             'status': self.status,
#             'created_at': self.created_at.isoformat(),
#             'sender': self.sender.to_dict() if self.sender else None,
#             'receiver': self.receiver.to_dict() if self.receiver else None
#         }
from extensions import db
from datetime import datetime

class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    # SỬA LẠI: Trỏ về bảng 'users' (số nhiều) thay vì 'user'
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    status = db.Column(db.String(20), default='pending') # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Không cần khai báo relationship ở đây nếu bên User đã có backref
    # Nhưng để an toàn cho to_dict, ta giữ nguyên logic truy cập qua backref từ User

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            # Lấy thông tin qua backref 'sender' và 'receiver' được định nghĩa ở User
            'sender': {
                'id': self.sender.id,
                'name': self.sender.name,
                'avatar_url': self.sender.avatar_url,
                'phone_number': self.sender.phone_number
            } if self.sender else None,
            'receiver': {
                'id': self.receiver.id,
                'name': self.receiver.name,
                'avatar_url': self.receiver.avatar_url,
                'phone_number': self.receiver.phone_number
            } if self.receiver else None
        }