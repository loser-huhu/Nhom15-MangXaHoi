from flask_socketio import emit
from flask_login import current_user
from datetime import datetime
from extensions import db  # Sử dụng extensions để tránh circular import
from models.post import Post, Like, Comment
from models.notification import Notification

def register_post_events(socketio):
    @socketio.on('like_post')
    def handle_like_post(data):
        try:
            post_id = data.get('post_id')
            post = Post.query.get(post_id)
            if not post:
                return

            # Xử lý Like/Unlike
            existing_like = Like.query.filter_by(
                user_id=current_user.id,
                post_id=post_id
            ).first()
            
            if existing_like:
                db.session.delete(existing_like)
                action = 'unliked'
            else:
                like = Like(user_id=current_user.id, post_id=post_id)
                db.session.add(like)
                action = 'liked'
                
                # Thông báo cho chủ bài viết
                if post.user_id != current_user.id:
                    notification = Notification(
                        user_id=post.user_id,
                        type='like',
                        data={
                            'user_id': current_user.id,
                            'user_name': current_user.name,
                            'post_id': post_id
                        }
                    )
                    db.session.add(notification)
                    emit('new_notification', notification.to_dict(), room=f'user_{post.user_id}')
            
            db.session.commit()
            
            # QUAN TRỌNG: Phát tín hiệu cho TOÀN BỘ mọi người bao gồm cả người gửi (include_self=True)
            emit('post_liked', {
                'post_id': post_id,
                'user_id': current_user.id,
                'action': action,
                'like_count': len(post.likes)
            }, broadcast=True, include_self=True)
            
        except Exception as e:
            db.session.rollback()
            print(f"Socket Like Error: {str(e)}")

    @socketio.on('comment_post')
    def handle_comment_post(data):
        try:
            post_id = data.get('post_id')
            content = data.get('content')
            if not content: return
            
            post = Post.query.get(post_id)
            if not post: return
            
            # Tạo comment mới
            comment = Comment(
                user_id=current_user.id,
                post_id=post_id,
                content=content
            )
            db.session.add(comment)
            
            # Thông báo cho chủ bài viết
            if post.user_id != current_user.id:
                notification = Notification(
                    user_id=post.user_id,
                    type='comment',
                    data={
                        'user_id': current_user.id,
                        'user_name': current_user.name,
                        'post_id': post_id
                    }
                )
                db.session.add(notification)
                emit('new_notification', notification.to_dict(), room=f'user_{post.user_id}')
            
            db.session.commit()
            
            # Phát tín hiệu bình luận mới cho tất cả mọi người
            emit('new_comment', {
                'post_id': post_id,
                'comment': comment.to_dict(),
                'comment_count': len(post.comments)
            }, broadcast=True, include_self=True)
            
        except Exception as e:
            db.session.rollback()
            print(f"Socket Comment Error: {str(e)}")