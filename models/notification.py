from datetime import datetime
from app import db
import json

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum('friend_request', 'friend_accept', 'like', 'comment', 
                            'message', name='notification_type'), nullable=False)
    data_json = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    @property
    def data(self):
        return json.loads(self.data_json) if self.data_json else {}
    
    @data.setter
    def data(self, data_dict):
        self.data_json = json.dumps(data_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'data': self.data,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }