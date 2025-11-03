from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from app.models.user import User
from app.models.booking import Booking
from app.schemas.user_schema import UserSchema
from app.schemas.booking_schema import BookingSchema
from app.extensions import db
from app.utils.role_required import role_required

traveler_bp = Blueprint("traveler_bp", __name__)
user_schema = UserSchema()
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

# Traveler profile
@traveler_bp.route("/profile", methods=["GET", "OPTIONS"])
@role_required("traveler")
def get_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    return user_schema.dump(user), 200

@traveler_bp.route("/profile", methods=["PATCH"])
@role_required("traveler")
def update_profile():
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

# Traveler bookings
@traveler_bp.route("/bookings", methods=["GET"])
@role_required("traveler")
def get_my_bookings():
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(traveler_id=int(user_id)).all()
    return bookings_schema.dump(bookings), 200

# Debug JWT endpoint
@traveler_bp.route("/debug-jwt", methods=["GET", "OPTIONS"])
@jwt_required()
def debug_jwt():
    user_id = get_jwt_identity()
    claims = get_jwt()
    return {
        "user_id": user_id,
        "claims": claims,
        "role": claims.get("role")
    }, 200
