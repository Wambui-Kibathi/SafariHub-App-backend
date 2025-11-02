from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.booking import Booking
from app.models.destination import Destination
from app.schemas.booking_schema import BookingSchema
from app.extensions import db
from app.utils.role_required import role_required

booking_bp = Blueprint("booking_bp", __name__)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

# Traveler: create booking
@booking_bp.route("/", methods=["POST"])
@role_required("traveler")
def create_booking():
    user_id = get_jwt_identity()
    data = request.get_json()
    destination = db.session.get(Destination, data["destination_id"])
    if not destination:
        return {"message": "Destination not found"}, 404

    total_days = (data["end_date"] - data["start_date"]).days + 1
    total_cost = total_days * destination.price

    booking = Booking(
        traveler_id=user_id,
        destination_id=data["destination_id"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        total_cost=total_cost
    )
    db.session.add(booking)
    db.session.commit()
    return booking_schema.dump(booking), 201

# GET all bookings (role filtered)
@booking_bp.route("/", methods=["GET"])
@role_required(["traveler", "guide", "admin"])
def get_bookings():
    user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    role = claims.get("role")

    if role == "traveler":
        bookings = Booking.query.filter_by(traveler_id=user_id).all()
    elif role == "guide":
        bookings = Booking.query.join(Destination).filter(Destination.guide_id==user_id).all()
    else:
        bookings = Booking.query.all()

    return bookings_schema.dump(bookings), 200

# GET single booking
@booking_bp.route("/<int:id>", methods=["GET"])
@role_required(["traveler", "guide", "admin"])
def get_booking(id):
    booking = db.session.get(Booking, id)
    if not booking:
        return {"message": "Booking not found"}, 404
    return booking_schema.dump(booking), 200

# DELETE booking (traveler can delete their own, admin can delete any)
@booking_bp.route("/<int:id>", methods=["DELETE"])
@role_required(["traveler", "admin"])
def delete_booking(id):
    user_id = get_jwt_identity()
    booking = db.session.get(Booking, id)
    if not booking:
        return {"message": "Booking not found"}, 404

    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    role = claims.get("role")

    if role == "traveler" and booking.traveler_id != user_id:
        return {"message": "Unauthorized"}, 403

    db.session.delete(booking)
    db.session.commit()
    return {"message": "Booking deleted successfully"}, 200