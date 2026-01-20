from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from models.user import User
from extensions import db  # THAY ĐỔI Ở ĐÂY

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        user = User.query.filter_by(phone_number=phone_number).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            user.update_last_seen()
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict()
            })
        
        return jsonify({
            'success': False,
            'message': 'Invalid phone number or password'
        }), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        password = data.get('password')
        name = data.get('name', '').strip()
        
        # Check if user exists
        if User.query.filter_by(phone_number=phone_number).first():
            return jsonify({
                'success': False,
                'message': 'Phone number already registered'
            }), 400
        
        # Create new user
        user = User(phone_number=phone_number, name=name)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user, remember=True)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': user.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    return jsonify({'authenticated': False})