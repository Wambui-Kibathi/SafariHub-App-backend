from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.destination import Destination
from app.models.booking import Booking
from app.schemas.user_schema import UserSchema
from app.schemas.destination_schema import DestinationSchema
from app.schemas.booking_schema import BookingSchema
from sqlalchemy import func

guide_bp = Blueprint('guide', __name__, url_prefix='/api/guides')

user_schema = UserSchema()
destination_schema = DestinationSchema()
destinations_schema = DestinationSchema(many=True)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)


def guide_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'guide':
            return jsonify({'error': 'Access denied. Guide role required.'}), 403
        
        return fn(*args, **kwargs)
    
    wrapper.__name__ = fn.__name__
    return wrapper


@guide_bp.route('/dashboard', methods=['GET'])
@guide_required
def get_dashboard():
    user_id = get_jwt_identity()
    
    total_destinations = Destination.query.filter_by(guide_id=user_id).count()
    
    guide_destinations = Destination.query.filter_by(guide_id=user_id).all()
    destination_ids = [dest.id for dest in guide_destinations]
    
    total_bookings = Booking.query.filter(Booking.destination_id.in_(destination_ids)).count()
    
    completed_bookings = Booking.query.filter(
        Booking.destination_id.in_(destination_ids),
        Booking.is_paid == True
    ).count()
    
    total_revenue = db.session.query(func.sum(Booking.total_cost)).filter(
        Booking.destination_id.in_(destination_ids),
        Booking.is_paid == True
    ).scalar() or 0
    
    recent_bookings = Booking.query.filter(
        Booking.destination_id.in_(destination_ids)
    ).order_by(Booking.created_at.desc()).limit(5).all()
    
    dashboard_data = {
        'total_destinations': total_destinations,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'total_revenue': float(total_revenue),
        'recent_bookings': bookings_schema.dump(recent_bookings)
    }
    
    return jsonify(dashboard_data), 200


@guide_bp.route('/destinations', methods=['GET'])
@guide_required
def get_guide_destinations():
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    destinations = Destination.query.filter_by(guide_id=user_id).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'destinations': destinations_schema.dump(destinations.items),
        'total': destinations.total,
        'pages': destinations.pages,
        'current_page': destinations.page
    }), 200


@guide_bp.route('/destinations/<int:destination_id>', methods=['GET'])
@guide_required
def get_single_destination(destination_id):
    user_id = get_jwt_identity()
    
    destination = Destination.query.filter_by(id=destination_id, guide_id=user_id).first()
    
    if not destination:
        return jsonify({'error': 'Destination not found or not assigned to you'}), 404
    
    return destination_schema.jsonify(destination), 200


@guide_bp.route('/bookings', methods=['GET'])
@guide_required
def get_guide_bookings():
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    guide_destinations = Destination.query.filter_by(guide_id=user_id).all()
    destination_ids = [dest.id for dest in guide_destinations]
    
    query = Booking.query.filter(Booking.destination_id.in_(destination_ids))
    
    if status == 'paid':
        query = query.filter_by(is_paid=True)
    elif status == 'pending':
        query = query.filter_by(is_paid=False)
    
    bookings = query.order_by(Booking.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'bookings': bookings_schema.dump(bookings.items),
        'total': bookings.total,
        'pages': bookings.pages,
        'current_page': bookings.page
    }), 200


@guide_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@guide_required
def get_single_booking(booking_id):
    user_id = get_jwt_identity()
    
    guide_destinations = Destination.query.filter_by(guide_id=user_id).all()
    destination_ids = [dest.id for dest in guide_destinations]
    
    booking = Booking.query.filter(
        Booking.id == booking_id,
        Booking.destination_id.in_(destination_ids)
    ).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found or not assigned to you'}), 404
    
    return booking_schema.jsonify(booking), 200


@guide_bp.route('/profile', methods=['GET'])
@guide_required
def get_guide_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return user_schema.jsonify(user), 200


@guide_bp.route('/profile', methods=['PUT'])
@guide_required
def update_guide_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        user.name = data['name']
    
    if 'email' in data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']
    
    if 'image_url' in data:
        user.image_url = data['image_url']
    
    if 'bio' in data:
        user.bio = data['bio']
    
    if 'phone' in data:
        user.phone = data['phone']
    
    if 'availability' in data:
        user.availability = data['availability']
    
    db.session.commit()
    
    return user_schema.jsonify(user), 200