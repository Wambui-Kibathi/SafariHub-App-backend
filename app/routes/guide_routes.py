from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app.models.booking import Booking
from app.models.destination import Destination
from app.schemas.user_schema import UserSchema
from app.schemas.booking_schema import BookingSchema
from app.schemas.destination_schema import DestinationSchema
from app.extensions import db
from app.utils.role_required import role_required

guide_bp = Blueprint("guide_bp", __name__)
user_schema = UserSchema()
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
destination_schema = DestinationSchema()
destinations_schema = DestinationSchema(many=True)

# Guide dashboard
@guide_bp.route("/dashboard", methods=["GET"])
@role_required("guide")
def guide_dashboard():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    total_bookings = Booking.query.join(Destination).filter(Destination.id==Booking.destination_id).count()
    return {
        "guide": user_schema.dump(user),
        "total_bookings": total_bookings
    }, 200

# Guide profile
@guide_bp.route("/profile", methods=["GET"])
@role_required("guide")
def get_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    return user_schema.dump(user), 200

@guide_bp.route("/profile", methods=["PATCH"])
@role_required("guide")
def update_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    data = request.get_json()

    if "full_name" in data:
        user.full_name = data["full_name"]
    if "password" in data:
        user.password = data["password"]
    if "profile_pic" in data:
        user.profile_pic = data["profile_pic"]

    db.session.commit()
    return user_schema.dump(user), 200

# Guide assigned destinations
@guide_bp.route("/destinations", methods=["GET"])
@role_required("guide")
def get_assigned_destinations():
    user_id = get_jwt_identity()
    destinations = Destination.query.filter_by(guide_id=user_id).all()
    return destinations_schema.dump(destinations), 200

# Guide view bookings for their destinations
@guide_bp.route("/bookings", methods=["GET"])
@role_required("guide")
def get_bookings():
    user_id = get_jwt_identity()
    bookings = Booking.query.join(Destination).filter(Destination.guide_id==user_id).all()
    return bookings_schema.dump(bookings), 200
