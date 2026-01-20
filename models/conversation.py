
# from extensions import db
# from datetime import datetime

# # Bảng phụ cho quan hệ nhiều-nhiều
# participants = db.Table('participants',
#     db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
#     db.Column('conversation_id', db.Integer, db.ForeignKey('conversations.id'), primary_key=True)
# )

# class Conversation(db.Model):
#     __tablename__ = 'conversations'
    
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100))
#     is_group = db.Column(db.Boolean, default=False)
#     admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
#     # Quan hệ với User (Dùng string 'User' để tránh lỗi Circular Import)
#     users = db.relationship('User', secondary=participants, lazy='subquery',
#                            backref=db.backref('conversations', lazy=True))
    
#     messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')

#     def to_dict(self, current_user_id):
#         name = self.title
#         avatar = 'default_group.png' # Ảnh mặc định nhóm
        
#         # Nếu là chat 1-1, lấy tên/avatar người kia
#         if not self.is_group:
#             other = next((u for u in self.users if u.id != current_user_id), None)
#             if other:
#                 name = other.name
#                 avatar = other.avatar_url
        
#         return {
#             'id': self.id,
#             'name': name,
#             'avatar': avatar,
#             'is_group': self.is_group,
#             'updated_at': self.updated_at.isoformat()
#         }

# class Message(db.Model):
#     __tablename__ = 'messages'
    
#     id = db.Column(db.Integer, primary_key=True)
#     conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
#     sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
#     content = db.Column(db.Text)
#     file_url = db.Column(db.String(500))
#     file_name = db.Column(db.String(255))
#     file_type = db.Column(db.String(50))
    
#     status = db.Column(db.String(20), default='sent')
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
#     # Quan hệ với User
#     sender = db.relationship('User', foreign_keys=[sender_id])

#     def to_dict(self):
#         return {
#             'id': self.id,
#             'conversation_id': self.conversation_id,
#             'sender_id': self.sender_id,
#             'sender_name': self.sender.name if self.sender else "Unknown",
#             'sender_avatar': self.sender.avatar_url if self.sender else "",
#             'content': self.content,
#             'file_url': self.file_url,
#             'file_name': self.file_name,
#             'file_type': self.file_type,
#             'created_at': self.created_at.isoformat()
#         }
# # # ok la
from extensions import db
from datetime import datetime

# Bảng phụ cho quan hệ nhiều-nhiều
participants = db.Table('participants',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversations.id'), primary_key=True)
)

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    is_group = db.Column(db.Boolean, default=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Quan hệ với User (Dùng string 'User' để tránh lỗi Circular Import)
    users = db.relationship('User', secondary=participants, lazy='subquery',
                           backref=db.backref('conversations', lazy=True))
    
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, current_user_id):
        name = self.title
        avatar = 'default_group.png' # Ảnh mặc định nhóm
        
        # Nếu là chat 1-1, lấy tên/avatar người kia
        if not self.is_group:
            other = next((u for u in self.users if u.id != current_user_id), None)
            if other:
                name = other.name
                avatar = other.avatar_url
        
        return {
            'id': self.id,
            'name': name,
            'avatar': avatar,
            'is_group': self.is_group,
            'updated_at': self.updated_at.isoformat()
        }


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text)
    file_url = db.Column(db.String(500))
    file_name = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    
    status = db.Column(db.String(20), default='sent')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- CÁC TRƯỜNG MỚI ---
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)
    is_recalled = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    pinned_at = db.Column(db.DateTime, nullable=True)
    
    sender = db.relationship('User', foreign_keys=[sender_id])

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.name if self.sender else "Unknown",
            'sender_avatar': self.sender.avatar_url if self.sender else "",
            'content': self.content,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'created_at': self.created_at.isoformat(),
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'is_recalled': self.is_recalled,
            'is_pinned': self.is_pinned,
            'pinned_at': self.pinned_at.isoformat() if self.pinned_at else None,
            'status': self.status
        }


class ConversationSettings(db.Model):
    __tablename__ = 'conversation_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    nickname = db.Column(db.String(100), nullable=True)  # Biệt danh đặt cho đối phương
    theme = db.Column(db.String(50), default='default')  # Theme cho cuộc trò chuyện này
    
    # Đảm bảo mỗi user chỉ có 1 setting cho 1 conversation
    __table_args__ = (db.UniqueConstraint('user_id', 'conversation_id', name='unique_conversation_settings'),)
    
    user = db.relationship('User', backref='conversation_settings')
    conversation = db.relationship('Conversation', backref='user_settings')

    # Thêm model Reaction
class Reaction(db.Model):
    __tablename__ = 'reactions'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, love, haha, wow, sad, angry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Quan hệ
    message = db.relationship('Message', backref='reactions')
    user = db.relationship('User', backref='user_reactions')
    
    __table_args__ = (db.UniqueConstraint('message_id', 'user_id', name='unique_message_user_reaction'),)