from flask_socketio import emit, join_room
from flask_login import current_user
from datetime import datetime
from app import db, socketio
from models.friend import FriendRequest
from models.notification import Notification

def register_friend_events(socketio):
    @socketio.on('send_friend_request')
    def handle_send_friend_request(data):
        try:
            receiver_id = data.get('receiver_id')
            
            if not current_user.is_authenticated:
                emit('error', {'message': 'Authentication required'})
                return
            
            # Check if user exists
            from models.user import User
            receiver = User.query.get(receiver_id)
            if not receiver:
                emit('error', {'message': 'User not found'})
                return
            
            # Check if request already exists
            existing_request = FriendRequest.query.filter(
                ((FriendRequest.sender_id == current_user.id) & 
                 (FriendRequest.receiver_id == receiver_id)) |
                ((FriendRequest.sender_id == receiver_id) & 
                 (FriendRequest.receiver_id == current_user.id))
            ).first()
            
            if existing_request:
                emit('error', {'message': 'Friend request already exists'})
                return
            
            # Create friend request
            friend_request = FriendRequest(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                status='pending'
            )
            
            db.session.add(friend_request)
            
            # Create notification
            notification = Notification(
                user_id=receiver_id,
                type='friend_request',
                data={
                    'sender_id': current_user.id,
                    'sender_name': current_user.name,
                    'request_id': friend_request.id
                }
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Emit to sender
            emit('friend_request_sent', {
                'request_id': friend_request.id,
                'receiver': receiver.to_dict(),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Emit to receiver
            emit('new_friend_request', {
                'request_id': friend_request.id,
                'sender': current_user.to_dict(),
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{receiver_id}')
            
            # Send notification
            emit('new_notification', notification.to_dict(), room=f'user_{receiver_id}')
            
        except Exception as e:
            db.session.rollback()
            emit('error', {'message': str(e)})
    
    @socketio.on('respond_friend_request')
    def handle_respond_friend_request(data):
        try:
            request_id = data.get('request_id')
            action = data.get('action')  # 'accept' or 'reject'
            
            if not current_user.is_authenticated:
                emit('error', {'message': 'Authentication required'})
                return
            
            friend_request = FriendRequest.query.get(request_id)
            if not friend_request:
                emit('error', {'message': 'Friend request not found'})
                return
            
            # Check authorization
            if friend_request.receiver_id != current_user.id:
                emit('error', {'message': 'Unauthorized'})
                return
            
            # Update status
            if action == 'accept':
                friend_request.status = 'accepted'
                notification_type = 'friend_accept'
                message = 'accepted your friend request'
            elif action == 'reject':
                friend_request.status = 'rejected'
                notification_type = 'friend_request'
                message = 'rejected your friend request'
            else:
                emit('error', {'message': 'Invalid action'})
                return
            
            # Create notification for sender
            notification = Notification(
                user_id=friend_request.sender_id,
                type=notification_type,
                data={
                    'user_id': current_user.id,
                    'user_name': current_user.name,
                    'request_id': friend_request.id
                }
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Emit response to receiver
            emit('friend_request_responded', {
                'request_id': request_id,
                'action': action,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Emit to sender
            emit('friend_request_response', {
                'request_id': request_id,
                'action': action,
                'user': current_user.to_dict(),
                'message': f'{current_user.name} {message}',
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{friend_request.sender_id}')
            
            # Send notification to sender
            emit('new_notification', notification.to_dict(), room=f'user_{friend_request.sender_id}')
            
        except Exception as e:
            db.session.rollback()
            emit('error', {'message': str(e)})
    
    @socketio.on('cancel_friend_request')
    def handle_cancel_friend_request(data):
        try:
            request_id = data.get('request_id')
            
            if not current_user.is_authenticated:
                emit('error', {'message': 'Authentication required'})
                return
            
            friend_request = FriendRequest.query.get(request_id)
            if not friend_request:
                emit('error', {'message': 'Friend request not found'})
                return
            
            # Check authorization
            if friend_request.sender_id != current_user.id:
                emit('error', {'message': 'Unauthorized'})
                return
            
            # Notify receiver
            emit('friend_request_cancelled', {
                'request_id': request_id,
                'sender': current_user.to_dict(),
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{friend_request.receiver_id}')
            
            # Delete request
            db.session.delete(friend_request)
            db.session.commit()
            
            emit('friend_request_cancelled_success', {
                'request_id': request_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            db.session.rollback()
            emit('error', {'message': str(e)})