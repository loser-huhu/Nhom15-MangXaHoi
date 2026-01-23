from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from models.user import User
from extensions import db
from datetime import datetime
import traceback

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Đăng nhập người dùng"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            }), 400
        
        phone_number = data.get('phone_number', '').strip()
        password = data.get('password', '')
        
        # Kiểm tra đầu vào
        if not phone_number:
            return jsonify({
                'success': False,
                'message': 'Vui lòng nhập số điện thoại'
            }), 400
        
        if not password:
            return jsonify({
                'success': False,
                'message': 'Vui lòng nhập mật khẩu'
            }), 400
        
        # Tìm người dùng
        user = User.query.filter_by(phone_number=phone_number).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Số điện thoại chưa được đăng ký'
            }), 401
        
        # Kiểm tra mật khẩu
        if not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Mật khẩu không đúng'
            }), 401
        
        # Kiểm tra tài khoản có bị khóa không
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Tài khoản đã bị khóa'
            }), 403
        
        # Cập nhật thời gian hoạt động cuối cùng - SỬA LỖI Ở ĐÂY
        try:
            if hasattr(user, 'update_last_seen'):
                user.update_last_seen()
            else:
                # Fallback nếu không có phương thức
                user.last_seen = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            print(f"Warning: Could not update last_seen: {e}")
            # Không fail nếu không cập nhật được last_seen
        
        # Đăng nhập người dùng
        login_user(user, remember=True)
        
        return jsonify({
            'success': True,
            'message': 'Đăng nhập thành công',
            'user': user.to_dict()
        })
        
    except Exception as e:
        print(f"Login error: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Lỗi hệ thống khi đăng nhập'
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Đăng ký người dùng mới"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            }), 400
        
        phone_number = data.get('phone_number', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # Kiểm tra đầu vào
        if not phone_number:
            return jsonify({
                'success': False,
                'message': 'Vui lòng nhập số điện thoại'
            }), 400
        
        if not password:
            return jsonify({
                'success': False,
                'message': 'Vui lòng nhập mật khẩu'
            }), 400
        
        # Kiểm tra định dạng số điện thoại (đơn giản)
        if not phone_number.isdigit() or len(phone_number) < 10:
            return jsonify({
                'success': False,
                'message': 'Số điện thoại không hợp lệ'
            }), 400
        
        # Kiểm tra độ mạnh mật khẩu - THÊM VALIDATION MỚI
        is_valid, error_message = User.validate_password_strength(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message
            }), 400
        
        # Kiểm tra số điện thoại đã tồn tại chưa
        existing_user = User.query.filter_by(phone_number=phone_number).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Số điện thoại đã được đăng ký'
            }), 400
        
        # Tạo người dùng mới
        user = User(phone_number=phone_number, name=name if name else phone_number)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Đăng nhập người dùng
        login_user(user, remember=True)
        
        return jsonify({
            'success': True,
            'message': 'Đăng ký thành công',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Lỗi hệ thống khi đăng ký'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Đăng xuất người dùng"""
    try:
        logout_user()
        return jsonify({
            'success': True,
            'message': 'Đăng xuất thành công'
        })
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'message': 'Lỗi khi đăng xuất'
        }), 500

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Kiểm tra trạng thái đăng nhập"""
    try:
        if current_user.is_authenticated:
            # Cập nhật last_seen cho mỗi lần kiểm tra
            try:
                current_user.update_last_seen()
            except:
                pass
                
            return jsonify({
                'authenticated': True,
                'user': current_user.to_dict()
            })
        
        return jsonify({
            'authenticated': False
        })
    except Exception as e:
        print(f"Check auth error: {e}")
        return jsonify({
            'authenticated': False
        })

@auth_bp.route('/current-user', methods=['GET'])
@login_required
def get_current_user():
    """Lấy thông tin người dùng hiện tại"""
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        })
    except Exception as e:
        print(f"Get current user error: {e}")
        return jsonify({
            'success': False,
            'message': 'Không thể lấy thông tin người dùng'
        }), 500