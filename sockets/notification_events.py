from flask_socketio import emit
from flask_login import current_user
from app import socketio

def register_notification_events(socketio):
    @socketio.on('get_unread_count')
    def handle_get_unread_count():
        try:
            if not current_user.is_authenticated:
                emit('error', {'message': 'Authentication required'})
                return
            
            from models.notification import Notification
            count = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).count()
            
            emit('unread_count', {
                'count': count,
                'user_id': current_user.id
            })
            
        except Exception as e:
            emit('error', {'message': str(e)})
    
    @socketio.on('mark_notification_read')
    def handle_mark_notification_read(data):
        try:
            notification_id = data.get('notification_id')
            
            if not current_user.is_authenticated:
                emit('error', {'message': 'Authentication required'})
                return
            
            from models.notification import Notification
            notification = Notification.query.get(notification_id)
            
            if notification and notification.user_id == current_user.id:
                notification.is_read = True
                from app import db
                db.session.commit()
                
                emit('notification_marked_read', {
                    'notification_id': notification_id
                })
            
        except Exception as e:
            emit('error', {'message': str(e)})