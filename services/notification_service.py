from models.notification import Notification
from app import db

class NotificationService:
    @staticmethod
    def create_notification(user_id, notification_type, data):
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            data=data
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def get_user_notifications(user_id, page=1, per_page=20):
        """Get notifications for user with pagination"""
        query = Notification.query.filter_by(user_id=user_id)
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'notifications': [n.to_dict() for n in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': notifications.page
        }
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications"""
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark notification as read"""
        notification = Notification.query.get(notification_id)
        
        if notification and notification.user_id == user_id:
            notification.is_read = True
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for user"""
        updated = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        return updated