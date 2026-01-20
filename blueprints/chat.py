from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db, socketio
from models.user import User
from models.conversation import Conversation, Message, ConversationSettings, Reaction  # Đã sửa import
from datetime import datetime
import os

chat_bp = Blueprint('chat', __name__)

# 1. LẤY DANH SÁCH CHAT (SIDEBAR)
@chat_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    try:
        conversations = current_user.conversations
        conversations.sort(key=lambda x: x.updated_at, reverse=True)
        
        results = []
        for conv in conversations:
            last_msg = Message.query.filter_by(conversation_id=conv.id).order_by(Message.created_at.desc()).first()
            results.append({
                'id': conv.id,
                **conv.to_dict(current_user.id),
                'last_message': last_msg.to_dict() if last_msg else None
            })
        return jsonify({'success': True, 'conversations': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 2. LẤY CHI TIẾT CHAT BẰNG ID HỘI THOẠI
@chat_bp.route('/detail/<int:conversation_id>', methods=['GET'])
@login_required
def get_chat_detail_by_id(conversation_id):
    try:
        conv = Conversation.query.get(conversation_id)
        if not conv or current_user not in conv.users:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
            
        messages = Message.query.filter_by(conversation_id=conv.id).order_by(Message.created_at.asc()).all()
        
        # Lấy conversation settings
        settings = ConversationSettings.query.filter_by(
            user_id=current_user.id,
            conversation_id=conversation_id
        ).first()
        
        # Lấy reactions cho mỗi tin nhắn
        messages_data = []
        for m in messages:
            msg_dict = m.to_dict()
            # Lấy reactions của tin nhắn
            reactions = Reaction.query.filter_by(message_id=m.id).all()
            # Nhóm reactions theo type
            reaction_summary = {}
            for r in reactions:
                reaction_summary[r.reaction_type] = reaction_summary.get(r.reaction_type, 0) + 1
            msg_dict['reactions'] = reaction_summary
            messages_data.append(msg_dict)
        
        conv_dict = {
            'id': conv.id,
            **conv.to_dict(current_user.id),
            'messages': messages_data,
            'users': [u.to_dict() for u in conv.users]
        }
        
        if settings:
            conv_dict['settings'] = {
                'nickname': settings.nickname,
                'theme': settings.theme,
                'background_image': settings.background_image
            }
        
        return jsonify({
            'success': True,
            'conversation': conv_dict
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 3. TÌM HOẶC TẠO CHAT 1-1
@chat_bp.route('/find-or-create/<int:target_user_id>', methods=['GET'])
@login_required
def find_or_create_chat(target_user_id):
    try:
        conv = Conversation.query.filter_by(is_group=False).filter(
            Conversation.users.any(id=current_user.id),
            Conversation.users.any(id=target_user_id)
        ).first()
        
        if not conv:
            conv = Conversation(is_group=False, updated_at=datetime.utcnow())
            target = User.query.get(target_user_id)
            conv.users.append(current_user)
            conv.users.append(target)
            db.session.add(conv)
            db.session.commit()
            
        return jsonify({'success': True, 'conversation_id': conv.id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 4. TẠO NHÓM
@chat_bp.route('/group/create', methods=['POST'])
@login_required
def create_group():
    try:
        data = request.get_json()
        name = data.get('name')
        members = data.get('members')
        
        if not name or not members:
            return jsonify({'success': False, 'message': 'Thiếu thông tin'}), 400
            
        group = Conversation(title=name, is_group=True, admin_id=current_user.id, updated_at=datetime.utcnow())
        group.users.append(current_user)
        
        for uid in members:
            u = User.query.get(uid)
            if u: 
                group.users.append(u)
            
        db.session.add(group)
        db.session.commit()
        return jsonify({'success': True, 'conversation_id': group.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 5. LẤY BẠN BÈ
@chat_bp.route('/friends', methods=['GET'])
@login_required
def get_friends_list():
    try:
        from models.friend import FriendRequest
        from sqlalchemy import or_
        
        # Lấy danh sách bạn bè thực sự
        friend_requests = FriendRequest.query.filter(
            ((FriendRequest.sender_id == current_user.id) | 
             (FriendRequest.receiver_id == current_user.id)),
            FriendRequest.status == 'accepted'
        ).all()
        
        friend_ids = []
        for fr in friend_requests:
            if fr.sender_id == current_user.id:
                friend_ids.append(fr.receiver_id)
            else:
                friend_ids.append(fr.sender_id)
        
        friends = User.query.filter(User.id.in_(friend_ids)).all()
        return jsonify({'friends': [u.to_dict() for u in friends]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 6. LẤY THÀNH VIÊN NHÓM
@chat_bp.route('/group/<int:group_id>/members', methods=['GET'])
@login_required
def get_group_members(group_id):
    try:
        group = Conversation.query.get(group_id)
        if not group or not group.is_group:
            return jsonify({'success': False, 'message': 'Nhóm không tồn tại'}), 404
            
        if current_user not in group.users:
            return jsonify({'success': False, 'message': 'Bạn không phải thành viên'}), 403
            
        members_data = []
        for u in group.users:
            members_data.append({
                'id': u.id,
                'name': u.name,
                'avatar_url': u.avatar_url,
                'phone_number': u.phone_number,
                'is_admin': u.id == group.admin_id
            })
            
        return jsonify({'success': True, 'members': members_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 7. RỜI NHÓM
@chat_bp.route('/group/leave', methods=['POST'])
@login_required
def leave_group():
    try:
        data = request.get_json()
        group_id = data.get('conversation_id')
        
        if not group_id:
            return jsonify({'success': False, 'message': 'Thiếu conversation_id'}), 400
            
        group = Conversation.query.get(group_id)
        if not group:
            return jsonify({'success': False, 'message': 'Không tìm thấy nhóm'}), 404
            
        if current_user in group.users:
            group.users.remove(current_user)
            
            if group.admin_id == current_user.id and group.users:
                group.admin_id = group.users[0].id
            
            db.session.commit()
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Bạn không ở trong nhóm này'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 8. XÓA HỘI THOẠI
@chat_bp.route('/conversation/<int:conv_id>', methods=['DELETE'])
@login_required
def delete_conversation(conv_id):
    try:
        conv = Conversation.query.get(conv_id)
        if not conv:
            return jsonify({'success': False}), 404
            
        if current_user in conv.users:
            conv.users.remove(current_user)
            db.session.commit()
            
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 9. THU HỒI TIN NHẮN
@chat_bp.route('/message/<int:message_id>/recall', methods=['POST'])
@login_required
def recall_message(message_id):
    try:
        msg = Message.query.get_or_404(message_id)
        
        if msg.sender_id != current_user.id:
            return jsonify({'success': False, 'message': 'Không có quyền thu hồi tin nhắn này'}), 403
            
        msg.is_recalled = True
        msg.content = '[Tin nhắn đã được thu hồi]'
        db.session.commit()
        
        try:
            socketio.emit('message_recalled', {
                'message_id': message_id,
                'conversation_id': msg.conversation_id
            }, room=str(msg.conversation_id))
        except:
            pass
            
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 10. CHỈNH SỬA TIN NHẮN
@chat_bp.route('/message/<int:message_id>/edit', methods=['PUT'])
@login_required
def edit_message(message_id):
    try:
        data = request.get_json()
        new_content = data.get('content', '').strip()
        
        if not new_content:
            return jsonify({'success': False, 'message': 'Nội dung không được trống'}), 400
            
        msg = Message.query.get_or_404(message_id)
        
        if msg.sender_id != current_user.id:
            return jsonify({'success': False, 'message': 'Không có quyền chỉnh sửa tin nhắn này'}), 403
            
        if msg.file_type:
            return jsonify({'success': False, 'message': 'Không thể chỉnh sửa tin nhắn có file'}), 400
            
        msg.content = new_content
        msg.is_edited = True
        msg.edited_at = datetime.utcnow()
        db.session.commit()
        
        try:
            socketio.emit('message_edited', {
                'message_id': message_id,
                'new_content': new_content,
                'conversation_id': msg.conversation_id
            }, room=str(msg.conversation_id))
        except:
            pass
            
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 11. GHIM/BỎ GHIM TIN NHẮN
@chat_bp.route('/message/<int:message_id>/toggle-pin', methods=['POST'])
@login_required
def toggle_pin_message(message_id):
    try:
        msg = Message.query.get_or_404(message_id)
        conv = Conversation.query.get_or_404(msg.conversation_id)
        
        if current_user not in conv.users:
            return jsonify({'success': False, 'message': 'Bạn không có quyền'}), 403
            
        # Nếu đang ghim thì bỏ ghim, nếu chưa ghim thì ghim (nhưng cho phép nhiều tin nhắn ghim)
        msg.is_pinned = not msg.is_pinned
        msg.pinned_at = datetime.utcnow() if msg.is_pinned else None
        
        db.session.commit()
        
        try:
            socketio.emit('message_pinned', {
                'message_id': message_id,
                'is_pinned': msg.is_pinned,
                'conversation_id': msg.conversation_id
            }, room=str(msg.conversation_id))
        except:
            pass
            
        return jsonify({'success': True, 'is_pinned': msg.is_pinned})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 12. ĐẶT BIỆT DANH
@chat_bp.route('/conversation/<int:conversation_id>/set-nickname', methods=['POST'])
@login_required
def set_nickname(conversation_id):
    try:
        data = request.get_json()
        target_user_id = data.get('target_user_id')
        nickname = data.get('nickname', '').strip()
        
        conv = Conversation.query.get_or_404(conversation_id)
        
        if current_user not in conv.users:
            return jsonify({'success': False, 'message': 'Bạn không có quyền'}), 403
            
        settings = ConversationSettings.query.filter_by(
            user_id=current_user.id,
            conversation_id=conversation_id
        ).first()
        
        if not settings:
            settings = ConversationSettings(
                user_id=current_user.id,
                conversation_id=conversation_id
            )
            db.session.add(settings)
        
        settings.nickname = nickname
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 13. ĐỔI THEME CHAT
@chat_bp.route('/conversation/<int:conversation_id>/set-theme', methods=['POST'])
@login_required
def set_conversation_theme(conversation_id):
    try:
        data = request.get_json()
        theme = data.get('theme', 'default').strip()
        
        conv = Conversation.query.get_or_404(conversation_id)
        
        if current_user not in conv.users:
            return jsonify({'success': False, 'message': 'Bạn không có quyền'}), 403
            
        settings = ConversationSettings.query.filter_by(
            user_id=current_user.id,
            conversation_id=conversation_id
        ).first()
        
        if not settings:
            settings = ConversationSettings(
                user_id=current_user.id,
                conversation_id=conversation_id,
                theme=theme
            )
            db.session.add(settings)
        else:
            settings.theme = theme
            
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 14. ĐỔI ẢNH NỀN CHAT
@chat_bp.route('/conversation/<int:conversation_id>/set-background', methods=['POST'])
@login_required
def set_background_image(conversation_id):
    try:
        if 'background' not in request.files:
            return jsonify({'success': False, 'message': 'Không có file'}), 400
            
        file = request.files['background']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Chưa chọn file'}), 400
            
        # Kiểm tra định dạng file
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        filename = file.filename.lower()
        if '.' not in filename or filename.rsplit('.', 1)[1] not in allowed_extensions:
            return jsonify({'success': False, 'message': 'Định dạng không hỗ trợ'}), 400
        
        # Lưu file
        from services.file_upload_service import FileUploadService
        bg_filename = FileUploadService.save_image(file, 'backgrounds')
        
        if not bg_filename:
            return jsonify({'success': False, 'message': 'Lỗi lưu file'}), 500
            
        # Lưu vào database
        settings = ConversationSettings.query.filter_by(
            user_id=current_user.id,
            conversation_id=conversation_id
        ).first()
        
        if not settings:
            settings = ConversationSettings(
                user_id=current_user.id,
                conversation_id=conversation_id,
                background_image=bg_filename
            )
            db.session.add(settings)
        else:
            settings.background_image = bg_filename
            
        db.session.commit()
        
        return jsonify({'success': True, 'filename': bg_filename})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 15. REACTION TIN NHẮN
@chat_bp.route('/message/<int:message_id>/reaction', methods=['POST'])
@login_required
def add_reaction(message_id):
    try:
        data = request.get_json()
        reaction_type = data.get('reaction_type', 'like')
        
        # Kiểm tra tin nhắn tồn tại
        message = Message.query.get_or_404(message_id)
        
        # Kiểm tra user có trong conversation không
        if current_user not in message.conversation.users:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        
        # Kiểm tra đã reaction chưa
        existing = Reaction.query.filter_by(
            message_id=message_id,
            user_id=current_user.id
        ).first()
        
        if existing:
            if existing.reaction_type == reaction_type:
                # Nếu cùng reaction type thì xóa (toggle)
                db.session.delete(existing)
                action = 'removed'
            else:
                # Nếu khác thì cập nhật
                existing.reaction_type = reaction_type
                action = 'updated'
        else:
            # Tạo reaction mới
            reaction = Reaction(
                message_id=message_id,
                user_id=current_user.id,
                reaction_type=reaction_type
            )
            db.session.add(reaction)
            action = 'added'
        
        db.session.commit()
        
        # Lấy tổng số reaction
        reactions = Reaction.query.filter_by(message_id=message_id).all()
        
        # Gộp theo type
        reaction_summary = {}
        for r in reactions:
            reaction_summary[r.reaction_type] = reaction_summary.get(r.reaction_type, 0) + 1
        
        # Gửi socket event
        try:
            socketio.emit('message_reacted', {
                'message_id': message_id,
                'user_id': current_user.id,
                'user_name': current_user.name,
                'reaction_type': reaction_type,
                'action': action,
                'reaction_summary': reaction_summary,
                'conversation_id': message.conversation_id
            }, room=str(message.conversation_id))
        except:
            pass
        
        return jsonify({
            'success': True,
            'action': action,
            'reaction_summary': reaction_summary,
            'total_reactions': len(reactions)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 16. XEM HỒ SƠ
@chat_bp.route('/user-profile/<int:user_id>', methods=['GET'])
@login_required
def get_user_profile(user_id):
    try:
        user = User.query.get_or_404(user_id)
        from models.post import Post
        from models.friend import FriendRequest
        from sqlalchemy import or_
        
        post_count = Post.query.filter_by(user_id=user_id).count()
        
        # Đếm số bạn bè
        friend_count = FriendRequest.query.filter(
            ((FriendRequest.sender_id == user_id) | 
             (FriendRequest.receiver_id == user_id)),
            FriendRequest.status == 'accepted'
        ).count()
        
        return jsonify({
            'success': True,
            'user': {
                **user.to_dict(),
                'post_count': post_count,
                'friend_count': friend_count,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500