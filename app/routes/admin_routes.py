from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.booking import Booking
from app.models.destination import Destination
from app.schemas.user_schema import UserSchema
from app.schemas.booking_schema import BookingSchema
from app.schemas.destination_schema import DestinationSchema
from app.extensions import db
from app.utils.role_required import role_required
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt

admin_bp = Blueprint("admin_bp", __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
destination_schema = DestinationSchema()
destinations_schema = DestinationSchema(many=True)

# Admin dashboard overview
@admin_bp.route("/dashboard", methods=["GET", "OPTIONS"])
@role_required("admin")
def admin_dashboard():
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    total_destinations = Destination.query.count()
    return {
        "total_users": total_users,
        "total_bookings": total_bookings,
        "total_destinations": total_destinations
    }, 200

# Admin profile
@admin_bp.route("/profile", methods=["GET", "OPTIONS"])
@role_required("admin")
def get_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    return user_schema.dump(user), 200

@admin_bp.route("/profile", methods=["POST", "PUT", "PATCH", "OPTIONS"])
@role_required("admin")
def update_admin_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    data = request.get_json()

    if "full_name" in data:
        user.full_name = data["full_name"]
    if "password" in data:
        user.password = data["password"]
    if "profile_pic" in data:
        user.profile_pic = data["profile_pic"]

    db.session.commit()
    return user_schema.dump(user), 200

# Debug JWT endpoint
@admin_bp.route("/debug-jwt", methods=["GET", "OPTIONS"])
@jwt_required()
def debug_jwt():
    user_id = get_jwt_identity()
    claims = get_jwt()
    return {
        "user_id": user_id,
        "claims": claims,
        "role": claims.get("role")
    }, 200

# Create admin user (for testing)
@admin_bp.route("/create-admin", methods=["POST", "OPTIONS"])
def create_admin():
    if User.query.filter_by(role="admin").first():
        return {"message": "Admin already exists"}, 400
    
    admin = User(
        full_name="Admin User",
        email="admin@safarihub.com",
        role="admin"
    )
    admin.password = "admin123"
    db.session.add(admin)
    db.session.commit()
    return {"message": "Admin created", "email": "admin@safarihub.com", "password": "admin123"}, 201

# Manage users
@admin_bp.route("/users", methods=["GET"])
@role_required("admin")
def get_users():
    users = User.query.all()
    return users_schema.dump(users), 200

@admin_bp.route("/users/<int:id>", methods=["PATCH"])
@role_required("admin")
def update_user(id):
    user = db.session.get(User, id)
    if not user:
        return {"message": "User not found"}, 404
    data = request.get_json()
    if "full_name" in data:
        user.full_name = data["full_name"]
    if "password" in data:
        user.password = data["password"]
    if "profile_pic" in data:
        user.profile_pic = data["profile_pic"]
    if "role" in data:
        user.role = data["role"]
    db.session.commit()
    return user_schema.dump(user), 200

@admin_bp.route("/users/<int:id>", methods=["DELETE"])
@role_required("admin")
def delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return {"message": "User not found"}, 404
    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted successfully"}, 200

# Manage bookings
@admin_bp.route("/bookings", methods=["GET"])
@role_required("admin")
def get_all_bookings():
    bookings = Booking.query.all()
    return bookings_schema.dump(bookings), 200

@admin_bp.route("/bookings/<int:id>", methods=["DELETE"])
@role_required("admin")
def delete_booking(id):
    booking = db.session.get(Booking, id)
    if not booking:
        return {"message": "Booking not found"}, 404
    db.session.delete(booking)
    db.session.commit()
    return {"message": "Booking deleted successfully"}, 200

# Manage destinations
@admin_bp.route("/destinations", methods=["GET"])
@role_required("admin")
def get_all_destinations():
    destinations = Destination.query.all()
    return destinations_schema.dump(destinations), 200