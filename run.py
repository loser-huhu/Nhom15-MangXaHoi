from app import create_app
from extensions import socketio

app = create_app()

if __name__ == '__main__':
    # Chế độ chạy mặc định phù hợp với Python 3.14
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)