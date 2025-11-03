from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.user import User
from app.schemas.payment_schema import PaymentSchema
from app.utils.role_required import role_required
from app.utils.paypal_service import create_order, capture_order

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

# Initialize a new PayPal payment
@payment_bp.route("/initialize", methods=["POST"])
@jwt_required()
def initialize_payment_route():
    data = request.get_json()
    booking_id = data.get("booking_id")

    if not booking_id:
        return jsonify({"error": "booking_id is required"}), 400

    booking = Booking.query.get_or_404(booking_id)
    current_user_id = get_jwt_identity()
    
    if booking.traveler_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403
    if booking.is_paid:
        return jsonify({"error": "Booking already paid"}), 400

    # Create PayPal order
    paypal_data = create_order(amount=booking.total_cost)

    # Create a pending Payment record
    payment = Payment(
        booking_id=booking.id,
        reference=paypal_data["id"],  
        amount=booking.total_cost,
        status="pending"
    )
    db.session.add(payment)
    db.session.commit()

    # Extract approval URL for frontend
    approval_url = next((link["href"] for link in paypal_data["links"] if link["rel"] == "approve"), None)
    return {
        "payment": payment_schema.dump(payment),
        "approval_url": approval_url
    }, 201

# Capture PayPal payment
@payment_bp.route("/capture-payment", methods=["POST"])
@jwt_required()
def capture_payment_route():
    data = request.get_json()
    order_id = data.get("orderID")

    if not order_id:
        return jsonify({"error": "orderID is required"}), 400

    payment = Payment.query.filter_by(reference=order_id).first_or_404()
    capture_data = capture_order(order_id)

    if capture_data["status"] == "COMPLETED":
        payment.status = "success"
        booking = Booking.query.get(payment.booking_id)
        booking.is_paid = True
        db.session.commit()
        return {"message": "Payment successful", "payment": payment_schema.dump(payment)}, 200
    else:
        payment.status = "failed"
        db.session.commit()
        return {"message": "Payment failed", "payment": payment_schema.dump(payment)}, 400

# Delete a payment (Admin only)
@payment_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return jsonify({"message": "Payment deleted"}), 200
