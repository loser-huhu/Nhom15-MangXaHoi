# from flask import Blueprint, request, jsonify
# from flask_login import login_required, current_user
# from datetime import datetime
# from app import db
# from models.post import Post, Like, Comment
# import json

# post_bp = Blueprint('post', __name__)

# @post_bp.route('/create', methods=['POST'])
# @login_required
# def create_post():
#     try:
#         content = request.form.get('content', '').strip()
#         images = []
        
#         # Handle multiple image uploads
#         for key in request.files:
#             if key.startswith('image_'):
#                 from services.file_upload_service import FileUploadService
#                 image_file = request.files[key]
#                 if image_file and image_file.filename:
#                     filename = FileUploadService.save_image(image_file, 'posts')
#                     if filename:
#                         images.append(filename)
        
#         # Create post
#         post = Post(
#             user_id=current_user.id,
#             content=content,
#             images=images
#         )
        
#         db.session.add(post)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Post created successfully',
#             'post': post.to_dict()
#         })
    
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @post_bp.route('/all', methods=['GET'])
# @login_required
# def get_posts():
#     try:
#         page = int(request.args.get('page', 1))
#         per_page = int(request.args.get('per_page', 10))
        
#         # Get posts from friends and self
#         from models.friend import FriendRequest
#         from sqlalchemy import or_
        
#         # Get friends IDs
#         friend_requests = FriendRequest.query.filter(
#             (FriendRequest.sender_id == current_user.id) | 
#             (FriendRequest.receiver_id == current_user.id),
#             FriendRequest.status == 'accepted'
#         ).all()
        
#         friend_ids = []
#         for fr in friend_requests:
#             if fr.sender_id == current_user.id:
#                 friend_ids.append(fr.receiver_id)
#             else:
#                 friend_ids.append(fr.sender_id)
        
#         # Include own posts
#         friend_ids.append(current_user.id)
        
#         # Query posts
#         posts = Post.query.filter(
#             Post.user_id.in_(friend_ids)
#         ).order_by(Post.created_at.desc()).paginate(
#             page=page, per_page=per_page, error_out=False
#         )
        
#         # Check if user liked each post
#         post_data = []
#         for post in posts.items:
#             post_dict = post.to_dict()
#             post_dict['is_liked'] = Like.query.filter_by(
#                 user_id=current_user.id,
#                 post_id=post.id
#             ).first() is not None
#             post_data.append(post_dict)
        
#         return jsonify({
#             'success': True,
#             'posts': post_data,
#             'total': posts.total,
#             'pages': posts.pages,
#             'current_page': posts.page
#         })
    
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @post_bp.route('/<int:post_id>/comments', methods=['GET'])
# @login_required
# def get_comments(post_id):
#     try:
#         post = Post.query.get_or_404(post_id)
        
#         comments = Comment.query.filter_by(
#             post_id=post_id
#         ).order_by(Comment.created_at.desc()).limit(50).all()
        
#         return jsonify({
#             'success': True,
#             'comments': [comment.to_dict() for comment in comments]
#         })
    
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @post_bp.route('/<int:post_id>/likes', methods=['GET'])
# @login_required
# def get_likes(post_id):
#     try:
#         likes = Like.query.filter_by(post_id=post_id).all()
        
#         # Get user info for each like
#         from models.user import User
#         like_data = []
#         for like in likes:
#             user = User.query.get(like.user_id)
#             if user:
#                 like_data.append(user.to_dict())
        
#         return jsonify({
#             'success': True,
#             'likes': like_data
#         })
    
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @post_bp.route('/<int:post_id>', methods=['DELETE'])
# @login_required
# def delete_post(post_id):
#     try:
#         post = Post.query.get_or_404(post_id)
        
#         # Check ownership
#         if post.user_id != current_user.id:
#             return jsonify({
#                 'success': False,
#                 'message': 'Unauthorized'
#             }), 403
        
#         # Delete associated images
#         from services.file_upload_service import FileUploadService
#         for image in post.images:
#             FileUploadService.delete_image(image)
        
#         db.session.delete(post)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Post deleted successfully'
#         })
    
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500


# ok

# from flask import Blueprint, request, jsonify
# from flask_login import login_required, current_user
# from extensions import db
# from models.post import Post, Like, Comment
# from models.friend import FriendRequest
# from models.user import User
# from services.file_upload_service import FileUploadService

# post_bp = Blueprint('post', __name__)

# @post_bp.route('/create', methods=['POST'])
# @login_required
# def create_post():
#     try:
#         content = request.form.get('content', '').strip()
#         images = []
        
#         # Xử lý upload nhiều ảnh (khớp với logic FormData image_0, image_1... ở frontend)
#         for key in request.files:
#             if key.startswith('image_'):
#                 file = request.files[key]
#                 if file and file.filename:
#                     # Lưu ảnh vào thư mục posts
#                     filename = FileUploadService.save_image(file, 'posts')
#                     if filename:
#                         images.append(filename)
        
#         # Nếu không có nội dung và không có ảnh thì báo lỗi
#         if not content and not images:
#             return jsonify({
#                 'success': False, 
#                 'message': 'Vui lòng nhập nội dung hoặc chọn ảnh'
#             }), 400

#         # Tạo bài viết mới
#         post = Post(
#             user_id=current_user.id,
#             content=content,
#             images=images
#         )
        
#         db.session.add(post)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Đăng bài thành công',
#             'post': post.to_dict()
#         })
    
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({
#             'success': False,
#             'message': f'Lỗi server: {str(e)}'
#         }), 500

# @post_bp.route('/all', methods=['GET'])
# @login_required
# def get_posts():
#     try:
#         # Kiểm tra xem có lọc theo user cụ thể không (Dùng cho trang Profile)
#         target_user_id = request.args.get('user_id', type=int)
        
#         if target_user_id:
#             # TRƯỜNG HỢP 1: Lấy bài viết của 1 người cụ thể (Profile)
#             posts = Post.query.filter_by(user_id=target_user_id)\
#                         .order_by(Post.created_at.desc())\
#                         .all()
#         else:
#             # TRƯỜNG HỢP 2: Lấy Newsfeed (Trang chủ - Index)
#             # Lấy danh sách ID bạn bè đã accept
#             friend_requests = FriendRequest.query.filter(
#                 ((FriendRequest.sender_id == current_user.id) | (FriendRequest.receiver_id == current_user.id)),
#                 FriendRequest.status == 'accepted'
#             ).all()
            
#             # Gom tất cả ID bạn bè + ID của chính mình
#             friend_ids = [fr.sender_id if fr.receiver_id == current_user.id else fr.receiver_id for fr in friend_requests]
#             friend_ids.append(current_user.id)
            
#             # Query bài viết của những người này
#             posts = Post.query.filter(Post.user_id.in_(friend_ids))\
#                         .order_by(Post.created_at.desc())\
#                         .all()
            
#         return jsonify({
#             'success': True,
#             'posts': [post.to_dict() for post in posts],
#             'total': len(posts)
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

# @post_bp.route('/<int:post_id>/comments', methods=['GET'])
# @login_required
# def get_comments(post_id):
#     try:
#         comments = Comment.query.filter_by(post_id=post_id)\
#                         .order_by(Comment.created_at.desc())\
#                         .all()
#         return jsonify({
#             'success': True,
#             'comments': [c.to_dict() for c in comments]
#         })
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)}), 500

# @post_bp.route('/<int:post_id>', methods=['DELETE'])
# @login_required
# def delete_post(post_id):
#     try:
#         post = Post.query.get_or_404(post_id)
        
#         # Chỉ cho phép xóa bài của chính mình
#         if post.user_id != current_user.id:
#             return jsonify({'success': False, 'message': 'Không có quyền xóa'}), 403
            
#         # Xóa ảnh vật lý liên quan (nếu cần thiết, tùy chọn)
#         # for img in post.images:
#         #     FileUploadService.delete_image(img)

#         db.session.delete(post)
#         db.session.commit()
        
#         return jsonify({'success': True, 'message': 'Đã xóa bài viết'})
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': str(e)}), 500
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.post import Post, Like, Comment
from models.friend import FriendRequest
from services.file_upload_service import FileUploadService

post_bp = Blueprint('post', __name__)

@post_bp.route('/create', methods=['POST'])
@login_required
def create_post():
    try:
        content = request.form.get('content', '').strip()
        images = []
        for key in request.files:
            if key.startswith('image_'):
                filename = FileUploadService.save_image(request.files[key], 'posts')
                if filename: images.append(filename)
        
        if not content and not images:
            return jsonify({'success': False, 'message': 'Nội dung trống!'})

        post = Post(user_id=current_user.id, content=content, images=images)
        db.session.add(post)
        db.session.commit()
        return jsonify({'success': True, 'post': post.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@post_bp.route('/all', methods=['GET'])
@login_required
def get_posts():
    try:
        target_id = request.args.get('user_id', type=int)
        if target_id:
            posts = Post.query.filter_by(user_id=target_id).order_by(Post.created_at.desc()).all()
        else:
            friends = FriendRequest.query.filter(
                ((FriendRequest.sender_id == current_user.id) | (FriendRequest.receiver_id == current_user.id)),
                FriendRequest.status == 'accepted'
            ).all()
            ids = [f.sender_id if f.receiver_id == current_user.id else f.receiver_id for f in friends]
            ids.append(current_user.id)
            posts = Post.query.filter(Post.user_id.in_(ids)).order_by(Post.created_at.desc()).all()

        return jsonify({'success': True, 'posts': [p.to_dict() for p in posts]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# --- QUAN TRỌNG: API LẤY COMMENT ---
@post_bp.route('/<int:post_id>/comments', methods=['GET'])
@login_required
def get_comments(post_id):
    try:
        # Lấy comment mới nhất trước
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
        return jsonify({
            'success': True, 
            'comments': [c.to_dict() for c in comments]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@post_bp.route('/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        db.session.delete(post)
        db.session.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})