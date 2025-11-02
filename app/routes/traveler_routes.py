from flask import Blueprint, request, jsonify
from app.models.booking import Booking, BookingStatus
from app.models.review import Review
from app.extensions import db
from datetime import datetime

traveler_bp = Blueprint('traveler', __name__)

@traveler_bp.route('/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.get_json()
        
        booking = Booking(
            user_id=data['user_id'],
            destination_id=data['destination_id'],
            booking_date=datetime.fromisoformat(data['booking_date']),
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            guests=data.get('guests', 1),
            total_price=data['total_price'],
            special_requests=data.get('special_requests')
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({'message': 'Booking created', 'booking': booking.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@traveler_bp.route('/bookings/<int:user_id>', methods=['GET'])
def get_user_bookings(user_id):
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return jsonify([booking.to_dict() for booking in bookings])

@traveler_bp.route('/bookings/<int:booking_id>/cancel', methods=['PUT'])
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status == BookingStatus.COMPLETED:
        return jsonify({'error': 'Cannot cancel completed booking'}), 400
    
    booking.status = BookingStatus.CANCELLED
    db.session.commit()
    
    return jsonify({'message': 'Booking cancelled', 'booking': booking.to_dict()})

@traveler_bp.route('/reviews', methods=['POST'])
def create_review():
    try:
        data = request.get_json()
        
        review = Review(
            user_id=data['user_id'],
            destination_id=data['destination_id'],
            booking_id=data['booking_id'],
            rating=data['rating'],
            comment=data.get('comment')
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({'message': 'Review created', 'review': review.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@traveler_bp.route('/reviews/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    reviews = Review.query.filter_by(user_id=user_id).all()
    return jsonify([review.to_dict() for review in reviews])