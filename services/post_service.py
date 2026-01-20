from models.post import Post, Like, Comment
from models.friend import FriendRequest
from extensions import db # SỬA: Dùng extensions thay vì app để tránh lỗi Circular Import
from sqlalchemy import desc

class PostService:
    @staticmethod
    def create_post(user_id, content, images=None):
        """Tạo bài viết mới"""
        post = Post(
            user_id=user_id,
            content=content,
            images=images or []
        )
        
        db.session.add(post)
        db.session.commit()
        return post
    
    @staticmethod
    def get_feed_posts(user_id, page=1, per_page=10):
        """Lấy bài viết cho bảng tin (bao gồm bài của bạn bè và chính mình)"""
        # 1. Lấy danh sách ID của bạn bè
        friend_requests = FriendRequest.query.filter(
            ((FriendRequest.sender_id == user_id) | 
             (FriendRequest.receiver_id == user_id)),
            FriendRequest.status == 'accepted'
        ).all()
        
        friend_ids = []
        for fr in friend_requests:
            if fr.sender_id == user_id:
                friend_ids.append(fr.receiver_id)
            else:
                friend_ids.append(fr.sender_id)
        
        # 2. Quan trọng: Luôn thêm ID của chính mình vào danh sách hiển thị
        if user_id not in friend_ids:
            friend_ids.append(user_id)
        
        # 3. Query bài viết từ Database
        # Sử dụng count() để tránh lỗi khi render giao diện rỗng
        query = Post.query.filter(Post.user_id.in_(friend_ids))
        posts_pagination = query.order_by(desc(Post.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 4. Xây dựng danh sách bài viết kèm trạng thái "Đã thích" hay chưa
        post_list = []
        for post in posts_pagination.items:
            post_dict = post.to_dict()
            # Kiểm tra xem user hiện tại đã like bài này chưa
            is_liked = Like.query.filter_by(
                user_id=user_id,
                post_id=post.id
            ).first() is not None
            
            post_dict['is_liked'] = is_liked
            post_list.append(post_dict)
        
        return {
            'success': True,
            'posts': post_list,
            'total': posts_pagination.total,
            'pages': posts_pagination.pages,
            'current_page': posts_pagination.page
        }
    
    @staticmethod
    def like_post(user_id, post_id):
        """Thực hiện Thích hoặc Bỏ thích"""
        like = Like.query.filter_by(
            user_id=user_id,
            post_id=post_id
        ).first()
        
        if like:
            db.session.delete(like)
            action = 'unliked'
        else:
            like = Like(user_id=user_id, post_id=post_id)
            db.session.add(like)
            action = 'liked'
        
        db.session.commit()
        return action
    
    @staticmethod
    def add_comment(user_id, post_id, content):
        """Thêm bình luận mới"""
        if not content or content.strip() == "":
            return None
            
        comment = Comment(
            user_id=user_id,
            post_id=post_id,
            content=content.strip()
        )
        
        db.session.add(comment)
        db.session.commit()
        return comment