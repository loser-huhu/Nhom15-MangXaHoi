from extensions import socketio, db
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from models.user import User
from models.conversation import Conversation, Message
from datetime import datetime

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        print(f"User {current_user.id} connected")
        join_room(f"user_{current_user.id}")

@socketio.on('join_conversation')
def handle_join_conversation(data):
    conversation_id = data.get('conversation_id')
    if current_user.is_authenticated and conversation_id:
        join_room(str(conversation_id))
        print(f"User {current_user.id} joined conversation {conversation_id}")

@socketio.on('send_message')
def handle_send_message(data):
    if not current_user.is_authenticated:
        return
    
    conversation_id = data.get('conversation_id')
    content = data.get('content', '').strip()
    file_url = data.get('file_url')
    file_name = data.get('file_name')
    file_type = data.get('file_type')
    
    # Kiểm tra conversation
    conversation = Conversation.query.get(conversation_id)
    if not conversation or current_user not in conversation.users:
        return
    
    # Tạo tin nhắn mới
    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=content if content else None,
        file_url=file_url,
        file_name=file_name,
        file_type=file_type,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.session.add(message)
    conversation.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Chuẩn bị data để gửi
    message_data = {
        'id': message.id,
        'conversation_id': message.conversation_id,
        'sender_id': message.sender_id,
        'sender_name': current_user.name,
        'sender_avatar': current_user.avatar_url,
        'content': message.content,
        'file_url': message.file_url,
        'file_name': message.file_name,
        'file_type': message.file_type,
        'is_recalled': message.is_recalled,
        'is_edited': message.is_edited,
        'is_pinned': message.is_pinned,
        'reactions': {},
        'created_at': message.created_at.isoformat()
    }
    
    # Gửi tin nhắn đến room
    emit('receive_message', message_data, room=str(conversation_id))
    
    # Gửi thông báo đến các user trong conversation
    for user in conversation.users:
        if user.id != current_user.id:
            emit('new_message_notification', {
                'conversation_id': conversation_id,
                'conversation_name': conversation.title if conversation.is_group else current_user.name,
                'message_preview': content[:50] if content else '[File]',
                'sender_name': current_user.name
            }, room=f"user_{user.id}")

@socketio.on('recall_message')
def handle_recall_message(data):
    if not current_user.is_authenticated:
        return
    
    message_id = data.get('message_id')
    message = Message.query.get(message_id)
    
    if message and message.sender_id == current_user.id:
        message.is_recalled = True
        message.content = '[Tin nhắn đã được thu hồi]'
        db.session.commit()
        
        emit('message_recalled', {
            'message_id': message_id,
            'conversation_id': message.conversation_id
        }, room=str(message.conversation_id))

@socketio.on('edit_message')
def handle_edit_message(data):
    if not current_user.is_authenticated:
        return
    
    message_id = data.get('message_id')
    new_content = data.get('content', '').strip()
    
    if not new_content:
        return
    
    message = Message.query.get(message_id)
    
    if message and message.sender_id == current_user.id and not message.file_type:
        message.content = new_content
        message.is_edited = True
        message.edited_at = datetime.utcnow()
        db.session.commit()
        
        emit('message_edited', {
            'message_id': message_id,
            'new_content': new_content,
            'conversation_id': message.conversation_id
        }, room=str(message.conversation_id))

@socketio.on('pin_message')
def handle_pin_message(data):
    if not current_user.is_authenticated:
        return
    
    message_id = data.get('message_id')
    action = data.get('action', 'pin')  # 'pin' or 'unpin'
    
    message = Message.query.get(message_id)
    if not message:
        return
    
    # Kiểm tra user có trong conversation không
    conversation = Conversation.query.get(message.conversation_id)
    if not conversation or current_user not in conversation.users:
        return
    
    message.is_pinned = (action == 'pin')
    message.pinned_at = datetime.utcnow() if action == 'pin' else None
    db.session.commit()
    
    emit('message_pinned', {
        'message_id': message_id,
        'is_pinned': message.is_pinned,
        'conversation_id': message.conversation_id,
        'pinned_at': message.pinned_at.isoformat() if message.pinned_at else None
    }, room=str(message.conversation_id))

@socketio.on('reaction_message')
def handle_reaction_message(data):
    if not current_user.is_authenticated:
        return
    
    message_id = data.get('message_id')
    reaction_type = data.get('reaction_type', 'like')
    
    from models.conversation import Reaction
    
    # Kiểm tra tin nhắn
    message = Message.query.get(message_id)
    if not message:
        return
    
    # Kiểm tra user có trong conversation không
    conversation = Conversation.query.get(message.conversation_id)
    if not conversation or current_user not in conversation.users:
        return
    
    # Kiểm tra reaction hiện có
    existing = Reaction.query.filter_by(
        message_id=message_id,
        user_id=current_user.id
    ).first()
    
    if existing:
        if existing.reaction_type == reaction_type:
            # Xóa reaction nếu trùng
            db.session.delete(existing)
            action = 'removed'
        else:
            # Cập nhật reaction
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
    
    # Lấy tổng reaction
    reactions = Reaction.query.filter_by(message_id=message_id).all()
    reaction_summary = {}
    for r in reactions:
        reaction_summary[r.reaction_type] = reaction_summary.get(r.reaction_type, 0) + 1
    
    emit('message_reacted', {
        'message_id': message_id,
        'user_id': current_user.id,
        'user_name': current_user.name,
        'reaction_type': reaction_type,
        'action': action,
        'reaction_summary': reaction_summary,
        'conversation_id': message.conversation_id
    }, room=str(message.conversation_id))

def register_chat_events(socketio_instance):
    """Đăng ký các event handler cho chat"""
    socketio_instance.on_event('connect', handle_connect)
    socketio_instance.on_event('join_conversation', handle_join_conversation)
    socketio_instance.on_event('send_message', handle_send_message)
    socketio_instance.on_event('recall_message', handle_recall_message)
    socketio_instance.on_event('edit_message', handle_edit_message)
    socketio_instance.on_event('pin_message', handle_pin_message)
    socketio_instance.on_event('reaction_message', handle_reaction_message)