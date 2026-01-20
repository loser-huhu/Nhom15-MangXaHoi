# from flask import Blueprint, request, jsonify
# from services.file_upload_service import FileUploadService

# upload_bp = Blueprint('upload', __name__)

# @upload_bp.route('/image', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return jsonify({'success': False, 'message': 'Không có file'}), 400
    
#     file = request.files['image']
#     if file.filename == '':
#         return jsonify({'success': False, 'message': 'Chưa chọn file'}), 400

#     filename = FileUploadService.save_image(file, 'messages')
    
#     if filename:
#         return jsonify({'success': True, 'filename': filename})
#     else:
#         return jsonify({'success': False, 'message': 'File không hợp lệ'}), 400
# ok
from flask import Blueprint, request, jsonify
from services.file_upload_service import FileUploadService
import os
from werkzeug.utils import secure_filename
import uuid
from flask import current_app

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Chưa chọn file'}), 400

    # Logic lưu file đơn giản
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Phân loại: Nếu là ảnh thì lưu vào images, file thì vào files (hoặc chung messages)
    # Ở đây ta lưu chung vào messages cho đơn giản
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'messages')
    os.makedirs(upload_path, exist_ok=True)
    
    try:
        file.save(os.path.join(upload_path, unique_filename))
        
        # Xác định loại file
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        file_type = 'image' if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp'] else 'file'
        
        return jsonify({
            'success': True, 
            'filename': unique_filename, 
            'original_name': filename,
            'type': file_type
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500