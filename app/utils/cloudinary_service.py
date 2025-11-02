import cloudinary
import cloudinary.uploader
import os

# Configure Cloudinary with your .env credentials
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_image_to_cloudinary(file, folder="safarihub_uploads"):
    """
    Upload a file object to Cloudinary.
    Returns the secure URL.
    """
    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type="image"
    )
    return result.get("secure_url")