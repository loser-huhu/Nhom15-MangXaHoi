# from flask import Blueprint, request, jsonify, send_from_directory
# from flask_login import login_required, current_user
# from extensions import db  # QUAN TRỌNG: Phải dùng extensions
# from models.user import User
# from services.file_upload_service import FileUploadService
# import os

# user_bp = Blueprint('user', __name__)

# @user_bp.route('/update', methods=['POST'])
# @login_required
# def update_profile():
#     try:
#         data = request.form
#         if 'name' in data:
#             current_user.name = data['name'].strip()
        
#         if 'avatar' in request.files:
#             avatar_file = request.files['avatar']
#             if avatar_file and avatar_file.filename:
#                 # Lưu ảnh mới (Service này đã được sửa để không lặp folder)
#                 filename = FileUploadService.save_image(avatar_file, 'avatars')
#                 if filename:
#                     current_user.avatar_url = filename
        
#         db.session.commit()
#         return jsonify({
#             'success': True,
#             'user': current_user.to_dict()
#         })
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': str(e)}), 500

# @user_bp.route('/update-theme', methods=['POST'])
# @login_required
# def update_theme():
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({'success': False, 'message': 'No data provided'}), 400

#         if 'theme' in data:
#             current_user.theme = data['theme']
#         if 'accent_color' in data:
#             current_user.accent_color = data['accent_color']
        
#         db.session.commit()
        
#         # Trả về mã 200 kèm data user mới nhất
#         return jsonify({
#             'success': True,
#             'message': 'Theme updated',
#             'user': current_user.to_dict()
#         })
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': str(e)}), 500

# @user_bp.route('/change-password', methods=['POST'])
# @login_required
# def change_password():
#     try:
#         data = request.get_json()
#         if not current_user.check_password(data.get('current_password')):
#             return jsonify({'success': False, 'message': 'Mật khẩu hiện tại sai'}), 400
        
#         current_user.set_password(data.get('new_password'))
#         db.session.commit()
#         return jsonify({'success': True})
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)}), 500

from flask import Blueprint, request, jsonify, send_from_directory
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from services.file_upload_service import FileUploadService
import os

user_bp = Blueprint('user', __name__)

# --- 1. LẤY THÔNG TIN PROFILE ---
@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# --- 2. CẬP NHẬT THÔNG TIN (Tên & Avatar) ---
@user_bp.route('/update', methods=['POST'])
@login_required
def update_profile():
    try:
        # Cập nhật tên
        if 'name' in request.form:
            current_user.name = request.form['name'].strip()
        
        # Cập nhật Avatar
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                # Lưu file và nhận về đường dẫn chuẩn "avatars/filename.ext"
                filename = FileUploadService.save_image(file, 'avatars')
                if filename:
                    current_user.avatar_url = filename
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật thành công',
            'user': current_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --- 3. ĐỔI GIAO DIỆN (Theme & Màu chủ đạo) ---
@user_bp.route('/update-theme', methods=['POST'])
@login_required
def update_theme():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Không có dữ liệu'}), 400
        
        # Cập nhật chế độ Sáng/Tối
        if 'theme' in data:
            current_user.theme = data['theme']
            
        # Cập nhật Màu chủ đạo (Accent Color)
        if 'accent_color' in data:
            current_user.accent_color = data['accent_color']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Đã lưu giao diện',
            'user': current_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --- 4. TÌM KIẾM BẠN BÈ ---
from models.friend import FriendRequest
from sqlalchemy import or_

@user_bp.route('/search', methods=['GET'])
@login_required
def search_users():
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            # Nếu không có query, trả về gợi ý ngẫu nhiên (trừ bản thân)
            users = User.query.filter(User.id != current_user.id).order_by(db.func.random()).limit(limit).all()
        else:
            # Tìm theo Tên hoặc Số điện thoại
            users = User.query.filter(
                (User.name.contains(query)) | 
                (User.phone_number.contains(query))
            ).filter(User.id != current_user.id).limit(limit).all()
        
        results = []
        for user in users:
            user_dict = user.to_dict()
            
            # --- LOGIC KIỂM TRA TRẠNG THÁI BẠN BÈ ---
            # 1. Kiểm tra xem có request nào giữa 2 người không
            freq = FriendRequest.query.filter(
                or_(
                    (FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == user.id),
                    (FriendRequest.sender_id == user.id) & (FriendRequest.receiver_id == current_user.id)
                )
            ).first()
            
            if freq:
                if freq.status == 'accepted':
                    user_dict['friendship_status'] = 'friends'
                elif freq.sender_id == current_user.id:
                    user_dict['friendship_status'] = 'request_sent'
                else:
                    user_dict['friendship_status'] = 'request_received'
            else:
                user_dict['friendship_status'] = 'none'
            # ----------------------------------------
            
            results.append(user_dict)
        
        return jsonify({
            'success': True,
            'users': results
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# --- 5. ĐỔI MẬT KHẨU ---
@user_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        data = request.get_json()
        current_pass = data.get('current_password')
        new_pass = data.get('new_password')
        
        if not current_user.check_password(current_pass):
            return jsonify({'success': False, 'message': 'Mật khẩu hiện tại không đúng'}), 400
        
        if len(new_pass) < 6:
            return jsonify({'success': False, 'message': 'Mật khẩu mới phải có ít nhất 6 ký tự'}), 400
            
        current_user.set_password(new_pass)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Đổi mật khẩu thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --- 6. ROUTES HỖ TRỢ LẤY FILE (Phòng hờ trường hợp static lỗi) ---
@user_bp.route('/avatar/<path:filename>')
def get_avatar(filename):
    return send_from_directory('static/uploads/avatars', filename)

@user_bp.route('/uploads/<path:filename>')
def get_upload(filename):
    return send_from_directory('static/uploads', filename)