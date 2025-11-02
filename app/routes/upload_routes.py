from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.utils.cloudinary_service import upload_image, delete_image
from werkzeug.utils import secure_filename
import os

upload_bp = Blueprint('uploads', __name__, url_prefix='/api/uploads')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file(file):
    if not file:
        return False, 'No file provided'
    
    if file.filename == '':
        return False, 'No file selected'
    
    if not allowed_file(file.filename):
        return False, 'Invalid file type. Only images are allowed (png, jpg, jpeg, gif, webp)'
    
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return False, f'File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024)}MB'
    
    return True, 'Valid file'


@upload_bp.route('/profile', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    
    is_valid, message = validate_file(file)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    filename = secure_filename(file.filename)
    
    folder = 'safarihub/profiles'
    public_id = f"user_{user_id}_{filename.rsplit('.', 1)[0]}"
    
    result = upload_image(file, folder=folder, public_id=public_id)
    
    if not result:
        return jsonify({'error': 'Failed to upload image to Cloudinary'}), 500
    
    image_url = result.get('secure_url')
    cloudinary_public_id = result.get('public_id')
    
    user.image_url = image_url
    user.cloudinary_public_id = cloudinary_public_id
    
    from app.extensions import db
    db.session.commit()
    
    return jsonify({
        'message': 'Profile picture uploaded successfully',
        'image_url': image_url,
        'public_id': cloudinary_public_id
    }), 200


@upload_bp.route('/destination', methods=['POST'])
@jwt_required()
def upload_destination_image():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Access denied. Admin role required.'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    
    is_valid, message = validate_file(file)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    filename = secure_filename(file.filename)
    
    destination_name = request.form.get('destination_name', 'destination')
    folder = 'safarihub/destinations'
    public_id = f"{destination_name.replace(' ', '_')}_{filename.rsplit('.', 1)[0]}"
    
    result = upload_image(file, folder=folder, public_id=public_id)
    
    if not result:
        return jsonify({'error': 'Failed to upload image to Cloudinary'}), 500
    
    image_url = result.get('secure_url')
    cloudinary_public_id = result.get('public_id')
    
    return jsonify({
        'message': 'Destination image uploaded successfully',
        'image_url': image_url,
        'public_id': cloudinary_public_id
    }), 200


@upload_bp.route('/<path:public_id>', methods=['DELETE'])
@jwt_required()
def delete_uploaded_image(public_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role != 'admin' and user.cloudinary_public_id != public_id:
        return jsonify({'error': 'Access denied. You can only delete your own images.'}), 403
    
    result = delete_image(public_id)
    
    if not result:
        return jsonify({'error': 'Failed to delete image from Cloudinary'}), 500
    
    if user.cloudinary_public_id == public_id:
        user.image_url = None
        user.cloudinary_public_id = None
        from app.extensions import db
        db.session.commit()
    
    return jsonify({
        'message': 'Image deleted successfully',
        'public_id': public_id
    }), 200