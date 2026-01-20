

from extensions import db
from datetime import datetime
from flask_login import current_user
import json

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text)
    _images = db.Column("images", db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

    @property
    def images(self):
        try: return json.loads(self._images) if self._images else []
        except: return []

    @images.setter
    def images(self, value):
        self._images = json.dumps(value)

    def to_dict(self):
        is_liked = False
        if current_user.is_authenticated:
            is_liked = any(like.user_id == current_user.id for like in self.likes)

        return {
            'id': self.id,
            'content': self.content,
            'images': self.images,
            'created_at': self.created_at.isoformat(),
            'like_count': len(self.likes),
            'comment_count': len(self.comments),
            'is_liked': is_liked,
            'author': {
                'id': self.author.id,
                'name': self.author.name,
                'avatar_url': self.author.avatar_url
            }
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Quan hệ User để lấy thông tin người comment
    user = db.relationship('User', backref=db.backref('user_comments', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'user': {
                'id': self.user.id,
                'name': self.user.name,
                'avatar_url': self.user.avatar_url
            }
        }

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)