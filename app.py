import os
from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
from extensions import db, login_manager, socketio

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # 1. CẤU HÌNH UPLOAD
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///zalo_clone.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Xác định đường dẫn tuyệt đối tới thư mục static/uploads
    basedir = os.path.abspath(os.path.dirname(__file__))
    upload_folder = os.path.join(basedir, 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Tự động tạo thư mục nếu chưa có
    os.makedirs(os.path.join(upload_folder, 'avatars'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'posts'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'messages'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'backgrounds'), exist_ok=True)

    # 2. KHỞI TẠO EXTENSIONS
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    login_manager.login_view = 'auth.login'

    with app.app_context():
        # Import Models
        from models.user import User
        from models.post import Post, Comment, Like
        from models.friend import FriendRequest
        from models.conversation import Conversation, Message, ConversationSettings, Reaction

        # Tạo bảng
        db.create_all()

        # Import Blueprints
        from blueprints.auth import auth_bp
        from blueprints.user import user_bp
        from blueprints.post import post_bp
        from blueprints.friend import friend_bp
        from blueprints.chat import chat_bp
        from blueprints.upload import upload_bp

        # REGISTER Blueprints
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(user_bp, url_prefix='/user')
        app.register_blueprint(post_bp, url_prefix='/post')
        app.register_blueprint(friend_bp, url_prefix='/friend')
        app.register_blueprint(chat_bp, url_prefix='/chat')
        app.register_blueprint(upload_bp, url_prefix='/upload')

        # Kích hoạt Socket Events
        from sockets.post_events import register_post_events
        from sockets.chat_events import register_chat_events
        register_post_events(socketio)
        register_chat_events(socketio)

    # Routes
    @app.route('/')
    def index():
        from flask_login import current_user
        if not current_user.is_authenticated: 
            return redirect('/login')
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        from flask_login import current_user
        if current_user.is_authenticated: 
            return redirect('/')
        return render_template('auth.html')

    @app.route('/profile')
    def profile_page():
        from flask_login import current_user
        if not current_user.is_authenticated: 
            return redirect('/login')
        return render_template('profile.html')

    @app.route('/friends')
    def friends_page():
        from flask_login import current_user
        if not current_user.is_authenticated: 
            return redirect('/login')
        return render_template('friends.html')

    @app.route('/chat')
    def chat_page():
        from flask_login import current_user
        if not current_user.is_authenticated: 
            return redirect('/login')
        return render_template('chat.html')

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, port=5000)