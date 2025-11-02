from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.schemas.user_schema import UserSchema
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    hashed_password = generate_password_hash(data.get('password'))
    
    new_user = User(
        name=data.get('name'),
        email=data.get('email'),
        password=hashed_password,
        role=data.get('role', 'traveler'),
        image_url=data.get('image_url')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return user_schema.jsonify(new_user), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'role': user.role},
        expires_delta=timedelta(days=7)
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user_schema.dump(user)
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return user_schema.jsonify(user), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
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
    if 'password' in data:
        user.password = generate_password_hash(data['password'])
    
    db.session.commit()
    
    return user_schema.jsonify(user), 200