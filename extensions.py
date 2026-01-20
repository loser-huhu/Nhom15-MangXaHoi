# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from flask_socketio import SocketIO

# db = SQLAlchemy()
# login_manager = LoginManager()
# socketio = SocketIO(cors_allowed_origins="*")
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
login_manager = LoginManager()
# Quan trọng: cors_allowed_origins="*" để tránh lỗi chặn kết nối
socketio = SocketIO(cors_allowed_origins="*")