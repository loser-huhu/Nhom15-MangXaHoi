from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from models.notification import Notification

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/list', methods=['GET'])
@login_required
def get_notifications():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        notifications = Notification.query.filter_by(
            user_id=current_user.id
        ).order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'notifications': [n.to_dict() for n in notifications.items],
            'total': notifications.total,
            'unread_count': Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).count()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@notification_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    try:
        notification = Notification.query.get_or_404(notification_id)
        
        # Check authorization
        if notification.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 403
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@notification_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    try:
        Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All notifications marked as read'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@notification_bp.route('/delete/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    try:
        notification = Notification.query.get_or_404(notification_id)
        
        # Check authorization
        if notification.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 403
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification deleted successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@notification_bp.route('/delete-all', methods=['DELETE'])
@login_required
def delete_all_notifications():
    try:
        Notification.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All notifications deleted'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500