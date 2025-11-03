from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from app.models.user import User
from app.extensions import db
from app.utils.role_required import role_required
from app.utils.cloudinary_service import upload_image_to_cloudinary

upload_bp = Blueprint("upload_bp", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload user profile picture
@upload_bp.route("/profile-picture", methods=["POST"])
@role_required(["traveler", "guide", "admin"])
def upload_profile_picture():
    if "file" not in request.files:
        return {"message": "No file part in request"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"message": "No selected file"}, 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Upload to Cloudinary using helper service
        try:
            cloud_url = upload_image_to_cloudinary(file, folder="safarihub_profiles")
        except Exception as e:
            return {"message": f"Upload failed: {str(e)}"}, 500

        # Update user's profile_pic
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        user.profile_pic = cloud_url
        db.session.commit()

        return {"message": "Profile picture uploaded successfully", "profile_pic": cloud_url}, 200
    else:
        return {"message": "Invalid file type"}, 400
