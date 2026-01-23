from extensions import db
from datetime import datetime

# Bảng trung gian cho quan hệ nhiều-nhiều giữa User và Conversation
conversation_users = db.Table('conversation_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversations.id'), primary_key=True)
)

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    is_group = db.Column(db.Boolean, default=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    avatar_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Quan hệ
    users = db.relationship('User', secondary=conversation_users, backref=db.backref('conversations', lazy=True))
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, current_user_id=None):
        data = {
            'id': self.id,
            'title': self.title,
            'is_group': self.is_group,
            'admin_id': self.admin_id,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Nếu là nhóm, tên là title, nếu là chat 1-1 thì tên là người còn lại
        if not self.is_group and current_user_id:
            other_user = None
            for user in self.users:
                if user.id != current_user_id:
                    other_user = user
                    break
            
            if other_user:
                data['name'] = other_user.name or "Người dùng"
                data['avatar'] = other_user.avatar_url
            else:
                data['name'] = "Người dùng"
                data['avatar'] = None
        else:
            data['name'] = self.title or "Nhóm chat"
            data['avatar'] = self.avatar_url
            
        return data

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text)
    file_url = db.Column(db.String(500))
    file_name = db.Column(db.String(500))
    file_type = db.Column(db.String(50))
    is_recalled = db.Column(db.Boolean, default=False)
    is_edited = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    pinned_at = db.Column(db.DateTime)
    edited_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Quan hệ
    sender = db.relationship('User', backref=db.backref('messages', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.name if self.sender else None,
            'sender_avatar': self.sender.avatar_url if self.sender else None,
            'content': self.content,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'is_recalled': self.is_recalled,
            'is_edited': self.is_edited,
            'is_pinned': self.is_pinned,
            'pinned_at': self.pinned_at.isoformat() if self.pinned_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class ConversationSettings(db.Model):
    __tablename__ = 'conversation_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    nickname = db.Column(db.String(100))
    theme = db.Column(db.String(50), default='default')
    background_image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Quan hệ
    user = db.relationship('User', backref=db.backref('conversation_settings', lazy=True))
    conversation = db.relationship('Conversation', backref=db.backref('settings', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'conversation_id': self.conversation_id,
            'nickname': self.nickname,
            'theme': self.theme,
            'background_image': self.background_image,
        }

class Reaction(db.Model):
    __tablename__ = 'reactions'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, love, haha, wow, sad, angry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Quan hệ
    message = db.relationship('Message', backref=db.backref('reactions', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('reactions', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'reaction_type': self.reaction_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }