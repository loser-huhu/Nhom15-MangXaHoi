from models.conversation import Conversation, Message
from models.user import User
from app import db
import json

class ChatService:
    @staticmethod
    def get_or_create_conversation(user1_id, user2_id):
        """Get existing conversation or create new one"""
        participants = sorted([user1_id, user2_id])
        
        conversation = Conversation.query.filter_by(
            participants_json=json.dumps(participants)
        ).first()
        
        if not conversation:
            conversation = Conversation(participants=participants)
            db.session.add(conversation)
            db.session.commit()
        
        return conversation
    
    @staticmethod
    def send_message(conversation_id, sender_id, content, image_url=None):
        """Send a message in conversation"""
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            image_url=image_url,
            status='delivered'
        )
        
        db.session.add(message)
        
        # Update conversation timestamp
        from datetime import datetime
        conversation = Conversation.query.get(conversation_id)
        conversation.last_message_at = datetime.utcnow()
        
        db.session.commit()
        return message
    
    @staticmethod
    def get_conversations(user_id):
        """Get all conversations for a user"""
        conversations = Conversation.query.filter(
            Conversation.participants_json.contains(str(user_id))
        ).order_by(Conversation.last_message_at.desc()).all()
        
        conversations_data = []
        for conv in conversations:
            conv_dict = conv.to_dict(user_id)
            
            # Get other user info
            other_user_id = conv.get_other_user(user_id)
            other_user = User.query.get(other_user_id)
            
            if other_user:
                conv_dict['other_user'] = other_user.to_dict()
                
                # Get unread count
                unread_count = Message.query.filter_by(
                    conversation_id=conv.id,
                    status='delivered'
                ).filter(Message.sender_id != user_id).count()
                
                conv_dict['unread_count'] = unread_count
            
            conversations_data.append(conv_dict)
        
        return conversations_data
    
    @staticmethod
    def mark_messages_as_seen(conversation_id, user_id):
        """Mark messages as seen in a conversation"""
        messages = Message.query.filter_by(
            conversation_id=conversation_id,
            status='delivered'
        ).filter(Message.sender_id != user_id).all()
        
        for message in messages:
            message.status = 'seen'
        
        db.session.commit()
        return len(messages)