from .auth import auth_bp
from .user import user_bp
from .post import post_bp
from .friend import friend_bp
from .chat import chat_bp
from .notification import notification_bp

__all__ = [
    'auth_bp',
    'user_bp',
    'post_bp',
    'friend_bp',
    'chat_bp',
    'notification_bp'
]