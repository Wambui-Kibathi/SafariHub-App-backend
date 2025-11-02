from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.user import User
from app.schemas.payment_schema import PaymentSchema
from app.utils.role_required import role_required
from app.utils.paystack_service import initialize_transaction, verify_transaction

payment_bp = Blueprint("payment_bp", __name__)
payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)

# GET all payments (Admin only)
@payment_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_payments():
    payments = Payment.query.all()
    return payments_schema.dump(payments), 200

# GET a single payment
@payment_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_payment(id):
    payment = Payment.query.get_or_404(id)
    current_user_id = get_jwt_identity()

    # Only the user who owns the booking or admin can access
    if payment.booking.user_id != current_user_id and not User.query.get(current_user_id).is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    return payment_schema.dump(payment), 200

# Initialize a new payment
@payment_bp.route("/initialize", methods=["POST"])
@jwt_required()
def initialize_payment_route():
    data = request.get_json()
    booking_id = data.get("booking_id")
    callback_url = data.get("callback_url")

    if not booking_id or not callback_url:
        return jsonify({"error": "booking_id and callback_url are required"}), 400

    booking = Booking.query.get_or_404(booking_id)

    # Ensure the current user owns the booking
    current_user_id = get_jwt_identity()
    if booking.traveler_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if booking.is_paid:
        return jsonify({"error": "Booking already paid"}), 400

    # Initialize Paystack transaction
    paystack_data = initialize_transaction(
        email=booking.user.email,
        amount=booking.total_cost,
        callback_url=callback_url
    )

    # Create a pending Payment record
    payment = Payment(
        booking_id=booking.id,
        reference=paystack_data["reference"],
        amount=booking.total_cost,
        status="pending"
    )
    db.session.add(payment)
    db.session.commit()

    return {
        "payment": payment_schema.dump(payment),
        "authorization_url": paystack_data["authorization_url"]
    }, 201

# Verify a payment by reference
@payment_bp.route("/verify/<string:reference>", methods=["GET"])
@jwt_required()
def verify_payment_route(reference):
    payment = Payment.query.filter_by(reference=reference).first_or_404()
    paystack_data = verify_transaction(reference)

    if paystack_data["status"] == "success":
        payment.status = "success"

        # Mark the booking as paid
        booking = Booking.query.get(payment.booking_id)
        booking.is_paid = True
        db.session.commit()
    else:
        payment.status = "failed"
        db.session.commit()

    return payment_schema.dump(payment), 200

# Delete a payment (Admin only)
@payment_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return jsonify({"message": "Payment deleted"}), 200
