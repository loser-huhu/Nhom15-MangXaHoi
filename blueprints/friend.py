# from flask import Blueprint, request, jsonify
# from flask_login import login_required, current_user
# from datetime import datetime
# from app import db
# from models.friend import FriendRequest
# from models.user import User

# friend_bp = Blueprint('friend', __name__)

# @friend_bp.route('/send-request', methods=['POST'])
# @login_required
# def send_friend_request():
#     try:
#         data = request.get_json()
#         receiver_id = data.get('receiver_id')
        
#         if receiver_id == current_user.id:
#             return jsonify({
#                 'success': False,
#                 'message': 'Cannot send friend request to yourself'
#             }), 400
        
#         # Check if user exists
#         receiver = User.query.get(receiver_id)
#         if not receiver:
#             return jsonify({
#                 'success': False,
#                 'message': 'User not found'
#             }), 404
        
#         # Check if request already exists
#         existing_request = FriendRequest.query.filter(
#             ((FriendRequest.sender_id == current_user.id) & 
#              (FriendRequest.receiver_id == receiver_id)) |
#             ((FriendRequest.sender_id == receiver_id) & 
#              (FriendRequest.receiver_id == current_user.id))
#         ).first()
        
#         if existing_request:
#             return jsonify({
#                 'success': False,
#                 'message': 'Friend request already exists'
#             }), 400
        
#         # Create new request
#         friend_request = FriendRequest(
#             sender_id=current_user.id,
#             receiver_id=receiver_id,
#             status='pending'
#         )
        
#         db.session.add(friend_request)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Friend request sent successfully',
#             'request': friend_request.to_dict()
#         })
    
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @friend_bp.route('/requests', methods=['GET'])
# @login_required
# def get_friend_requests():
#     try:
#         # Get pending requests received
#         requests_received = FriendRequest.query.filter_by(
#             receiver_id=current_user.id,
#             status='pending'
#         ).order_by(FriendRequest.created_at.desc()).all()
        
#         # Get pending requests sent
#         requests_sent = FriendRequest.query.filter_by(
#             sender_id=current_user.id,
#             status='pending'
#         ).order_by(FriendRequest.created_at.desc()).all()
        
#         return jsonify({
#             'success': True,
#             'received': [req.to_dict() for req in requests_received],
#             'sent': [req.to_dict() for req in requests_sent]
#         })
    
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @friend_bp.route('/requests/<int:request_id>/respond', methods=['POST'])
# @login_required
# def respond_friend_request(request_id):
#     try:
#         data = request.get_json()
#         action = data.get('action')  # 'accept' or 'reject'
        
#         friend_request = FriendRequest.query.get_or_404(request_id)
        
#         # Check authorization
#         if friend_request.receiver_id != current_user.id:
#             return jsonify({
#                 'success': False,
#                 'message': 'Unauthorized'
#             }), 403
        
#         if action == 'accept':
#             friend_request.status = 'accepted'
#         elif action == 'reject':
#             friend_request.status = 'rejected'
#         else:
#             return jsonify({
#                 'success': False,
#                 'message': 'Invalid action'
#             }), 400
        
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': f'Friend request {action}ed successfully',
#             'request': friend_request.to_dict()
#         })
    
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @friend_bp.route('/list', methods=['GET'])
# @login_required
# def get_friends():
#     try:
#         friend_requests = FriendRequest.query.filter(
#             ((FriendRequest.sender_id == current_user.id) | 
#              (FriendRequest.receiver_id == current_user.id)),
#             FriendRequest.status == 'accepted'
#         ).all()
        
#         friends = []
#         for fr in friend_requests:
#             if fr.sender_id == current_user.id:
#                 friend = User.query.get(fr.receiver_id)
#             else:
#                 friend = User.query.get(fr.sender_id)
            
#             if friend:
#                 friends.append(friend.to_dict())
        
#         return jsonify({
#             'success': True,
#             'friends': friends
#         })
    
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @friend_bp.route('/online', methods=['GET'])
# @login_required
# def get_online_friends():
#     try:
#         from datetime import timedelta
#         from sqlalchemy import or_
        
#         # Get all friends
#         friend_requests = FriendRequest.query.filter(
#             ((FriendRequest.sender_id == current_user.id) | 
#              (FriendRequest.receiver_id == current_user.id)),
#             FriendRequest.status == 'accepted'
#         ).all()
        
#         online_friends = []
#         time_threshold = datetime.utcnow() - timedelta(minutes=5)
        
#         for fr in friend_requests:
#             if fr.sender_id == current_user.id:
#                 friend = User.query.get(fr.receiver_id)
#             else:
#                 friend = User.query.get(fr.sender_id)
            
#             if friend and friend.last_seen and friend.last_seen > time_threshold:
#                 online_friends.append(friend.to_dict())
        
#         return jsonify({
#             'success': True,
#             'friends': online_friends
#         })
    
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @friend_bp.route('/requests/<int:request_id>/cancel', methods=['DELETE'])
# @login_required
# def cancel_friend_request(request_id):
#     try:
#         friend_request = FriendRequest.query.get_or_404(request_id)
        
#         # Check authorization
#         if friend_request.sender_id != current_user.id:
#             return jsonify({
#                 'success': False,
#                 'message': 'Unauthorized'
#             }), 403
        
#         db.session.delete(friend_request)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Friend request cancelled successfully'
#         })
    
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db, socketio
from models.user import User
from models.friend import FriendRequest
from sqlalchemy import or_

friend_bp = Blueprint('friend', __name__)

# --- 1. GỬI LỜI MỜI KẾT BẠN ---
@friend_bp.route('/send-request', methods=['POST'])
@login_required
def send_friend_request():
    try:
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        
        if not receiver_id:
            return jsonify({'success': False, 'message': 'Thiếu ID người nhận'}), 400
            
        if int(receiver_id) == current_user.id:
            return jsonify({'success': False, 'message': 'Không thể kết bạn với chính mình'}), 400

        # Kiểm tra xem đã là bạn hoặc đã gửi lời mời chưa
        existing_request = FriendRequest.query.filter(
            or_(
                (FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == receiver_id),
                (FriendRequest.sender_id == receiver_id) & (FriendRequest.receiver_id == current_user.id)
            )
        ).first()

        if existing_request:
            if existing_request.status == 'accepted':
                return jsonify({'success': False, 'message': 'Hai người đã là bạn bè'})
            elif existing_request.sender_id == current_user.id:
                return jsonify({'success': False, 'message': 'Bạn đã gửi lời mời rồi'})
            else:
                return jsonify({'success': False, 'message': 'Người này đã gửi lời mời cho bạn, hãy chấp nhận nhé'})

        # Tạo lời mời mới
        new_request = FriendRequest(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            status='pending'
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        # Gửi thông báo Realtime cho người nhận
        # (Nếu bạn chưa cấu hình socket room thì dòng này sẽ bị bỏ qua không gây lỗi)
        try:
            socketio.emit('new_friend_request', {
                'sender': current_user.to_dict()
            }, room=f"user_{receiver_id}")
        except:
            pass

        return jsonify({'success': True, 'message': 'Đã gửi lời mời kết bạn'})

    except Exception as e:
        db.session.rollback()
        print(f"Lỗi gửi kết bạn: {e}") # In lỗi ra terminal để dễ debug
        return jsonify({'success': False, 'message': 'Lỗi server khi gửi lời mời'}), 500

# --- 2. DANH SÁCH BẠN BÈ ---
@friend_bp.route('/list', methods=['GET'])
@login_required
def get_friend_list():
    try:
        # Lấy tất cả request đã accepted
        friends_query = FriendRequest.query.filter(
            ((FriendRequest.sender_id == current_user.id) | (FriendRequest.receiver_id == current_user.id)),
            FriendRequest.status == 'accepted'
        ).all()
        
        friends_list = []
        for req in friends_query:
            # Nếu mình là sender thì bạn là receiver và ngược lại
            friend_user = req.receiver if req.sender_id == current_user.id else req.sender
            friends_list.append(friend_user.to_dict())
            
        return jsonify({'success': True, 'friends': friends_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# --- 3. DANH SÁCH LỜI MỜI (Gửi đi & Nhận được) ---
@friend_bp.route('/requests', methods=['GET'])
@login_required
def get_friend_requests():
    try:
        # Lời mời nhận được (người khác gửi cho mình)
        received = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()
        
        # Lời mời đã gửi (mình gửi cho người khác)
        sent = FriendRequest.query.filter_by(sender_id=current_user.id, status='pending').all()
        
        return jsonify({
            'success': True,
            'received': [req.to_dict() for req in received],
            'sent': [req.to_dict() for req in sent]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# --- 4. PHẢN HỒI LỜI MỜI (Chấp nhận / Từ chối) ---
@friend_bp.route('/requests/<int:request_id>/respond', methods=['POST'])
@login_required
def respond_friend_request(request_id):
    try:
        data = request.get_json()
        action = data.get('action') # 'accept' hoặc 'reject'
        
        req = FriendRequest.query.get_or_404(request_id)
        
        # Chỉ người nhận mới được quyền chấp nhận/từ chối
        if req.receiver_id != current_user.id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
            
        if action == 'accept':
            req.status = 'accepted'
            msg = 'Đã chấp nhận kết bạn'
            # Socket thông báo cho người gửi biết
            try:
                socketio.emit('friend_request_response', {
                    'action': 'accept',
                    'message': f'{current_user.name} đã chấp nhận lời mời kết bạn',
                    'user': current_user.to_dict()
                }, room=f"user_{req.sender_id}")
            except: pass
            
        elif action == 'reject':
            db.session.delete(req)
            msg = 'Đã từ chối kết bạn'
        else:
            return jsonify({'success': False, 'message': 'Hành động không hợp lệ'}), 400
            
        db.session.commit()
        return jsonify({'success': True, 'message': msg})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --- 5. HỦY LỜI MỜI / HỦY KẾT BẠN ---
@friend_bp.route('/requests/<int:request_id>/cancel', methods=['DELETE'])
@login_required
def cancel_friend_request(request_id):
    try:
        req = FriendRequest.query.get_or_404(request_id)
        
        # Kiểm tra quyền: Phải là người trong cuộc mới được hủy
        if req.sender_id != current_user.id and req.receiver_id != current_user.id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
            
        db.session.delete(req)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Đã hủy'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --- 6. BẠN BÈ ONLINE ---
@friend_bp.route('/online', methods=['GET'])
@login_required
def get_online_friends():
    try:
        # Lấy danh sách bạn bè trước
        friends_requests = FriendRequest.query.filter(
            ((FriendRequest.sender_id == current_user.id) | (FriendRequest.receiver_id == current_user.id)),
            FriendRequest.status == 'accepted'
        ).all()
        
        online_friends = []
        for req in friends_requests:
            friend = req.receiver if req.sender_id == current_user.id else req.sender
            # Logic check online đơn giản (có thể nâng cấp sau với Redis hoặc Last_seen)
            # Tạm thời trả về list friends
            online_friends.append(friend.to_dict())
            
        return jsonify({'success': True, 'friends': online_friends})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500