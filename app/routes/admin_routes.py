from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.booking import Booking
from app.models.destination import Destination
from app.schemas.user_schema import UserSchema
from app.schemas.booking_schema import BookingSchema
from app.schemas.destination_schema import DestinationSchema
from app.extensions import db
from app.utils.role_required import role_required

admin_bp = Blueprint("admin_bp", __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
destination_schema = DestinationSchema()
destinations_schema = DestinationSchema(many=True)

# Admin dashboard overview
@admin_bp.route("/dashboard", methods=["GET"])
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