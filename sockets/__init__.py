from .chat_events import register_chat_events
from .post_events import register_post_events
from .friend_events import register_friend_events
from .notification_events import register_notification_events

__all__ = [
    'register_chat_events',
    'register_post_events',
    'register_friend_events',
    'register_notification_events'
]