from models.user import User
from models.friend import FriendRequest
from app import db
from sqlalchemy import or_

class UserService:
    @staticmethod
    def search_users(query, current_user_id, limit=20):
        """Search users by phone number or name"""
        if not query:
            return []
        
        # Search by phone or name, exclude current user
        users = User.query.filter(
            (User.phone_number.contains(query)) | 
            (User.name.contains(query))
        ).filter(User.id != current_user_id).limit(limit).all()
        
        # Add friendship status
        result = []
        for user in users:
            user_dict = user.to_dict()
            user_dict['friendship_status'] = UserService.get_friendship_status(
                current_user_id, user.id
            )
            result.append(user_dict)
        
        return result
    
    @staticmethod
    def get_friendship_status(user1_id, user2_id):
        """Get friendship status between two users"""
        if user1_id == user2_id:
            return 'self'
        
        friend_request = FriendRequest.query.filter(
            ((FriendRequest.sender_id == user1_id) & 
             (FriendRequest.receiver_id == user2_id)) |
            ((FriendRequest.sender_id == user2_id) & 
             (FriendRequest.receiver_id == user1_id))
        ).first()
        
        if not friend_request:
            return 'none'
        
        if friend_request.status == 'pending':
            if friend_request.sender_id == user1_id:
                return 'request_sent'
            else:
                return 'request_received'
        elif friend_request.status == 'accepted':
            return 'friends'
        else:
            return 'rejected'
    
    @staticmethod
    def get_friends(user_id):
        """Get all friends of a user"""
        friend_requests = FriendRequest.query.filter(
            ((FriendRequest.sender_id == user_id) | 
             (FriendRequest.receiver_id == user_id)),
            FriendRequest.status == 'accepted'
        ).all()
        
        friends = []
        for fr in friend_requests:
            if fr.sender_id == user_id:
                friend = User.query.get(fr.receiver_id)
            else:
                friend = User.query.get(fr.sender_id)
            
            if friend:
                friends.append(friend)
        
        return friends
    
    @staticmethod
    def get_online_friends(user_id):
        """Get online friends"""
        from datetime import datetime, timedelta
        
        friends = UserService.get_friends(user_id)
        time_threshold = datetime.utcnow() - timedelta(minutes=5)
        
        return [friend for friend in friends 
                if friend.last_seen and friend.last_seen > time_threshold]