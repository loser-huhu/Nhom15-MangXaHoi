from flask_socketio import emit, join_room
from flask_login import current_user
from extensions import db, socketio
from models.conversation import Conversation, Message
from datetime import datetime

def register_chat_events(socketio_instance):
    @socketio_instance.on('connect')
    def handle_connect():
        if not current_user.is_authenticated: 
            return False

    @socketio_instance.on('join_conversation')
    def on_join(data):
        if not current_user.is_authenticated: 
            return
        room = data.get('conversation_id')
        join_room(room)

    @socketio_instance.on('send_message')
    def handle_send_message(data):
        if not current_user.is_authenticated: 
            return
        try:
            conversation_id = data.get('conversation_id')
            content = data.get('content')
            file_url = data.get('file_url')
            file_name = data.get('file_name')
            file_type = data.get('file_type')
            
            conv = Conversation.query.get(conversation_id)
            if not conv: 
                return

            msg = Message(
                conversation_id=conv.id,
                sender_id=current_user.id,
                content=content,
                file_url=file_url,
                file_name=file_name,
                file_type=file_type,
                status='sent',
                created_at=datetime.utcnow()
            )
            
            conv.updated_at = datetime.utcnow()
            db.session.add(msg)
            db.session.commit()
            
            emit('receive_message', msg.to_dict(), room=conversation_id)
            
        except Exception as e:
            print(f"Chat Error: {e}")

    @socketio_instance.on('recall_message')
    def handle_recall_message(data):
        if not current_user.is_authenticated: 
            return
        try:
            message_id = data.get('message_id')
            msg = Message.query.get(message_id)
            if not msg: 
                return
            
            if msg.sender_id != current_user.id:
                emit('error', {'message': 'Không có quyền thu hồi'})
                return
                
            msg.is_recalled = True
            msg.content = '[Tin nhắn đã được thu hồi]'
            db.session.commit()
            
            emit('message_recalled', {
                'message_id': message_id,
                'conversation_id': msg.conversation_id
            }, room=str(msg.conversation_id))
            
        except Exception as e:
            print(f"Recall error: {e}")

    @socketio_instance.on('edit_message')
    def handle_edit_message(data):
        if not current_user.is_authenticated: 
            return
        try:
            message_id = data.get('message_id')
            new_content = data.get('content', '').strip()
            
            if not new_content: 
                return
            
            msg = Message.query.get(message_id)
            if not msg: 
                return
            
            if msg.sender_id != current_user.id:
                emit('error', {'message': 'Không có quyền chỉnh sửa'})
                return
                
            msg.content = new_content
            msg.is_edited = True
            msg.edited_at = datetime.utcnow()
            db.session.commit()
            
            emit('message_edited', {
                'message_id': message_id,
                'new_content': new_content,
                'conversation_id': msg.conversation_id
            }, room=str(msg.conversation_id))
            
        except Exception as e:
            print(f"Edit error: {e}")

    @socketio_instance.on('pin_message')
    def handle_pin_message(data):
        if not current_user.is_authenticated: 
            return
        try:
            message_id = data.get('message_id')
            msg = Message.query.get(message_id)
            if not msg: 
                return
            
            conv = Conversation.query.get(msg.conversation_id)
            if not conv or current_user not in conv.users:
                emit('error', {'message': 'Không có quyền'})
                return
                
            msg.is_pinned = not msg.is_pinned
            msg.pinned_at = datetime.utcnow() if msg.is_pinned else None
            db.session.commit()
            
            emit('message_pinned', {
                'message_id': message_id,
                'is_pinned': msg.is_pinned,
                'conversation_id': msg.conversation_id
            }, room=str(msg.conversation_id))
            
        except Exception as e:
            print(f"Pin error: {e}")