from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from app.models.user import User
from app.schemas.user_schema import UserSchema
from app.extensions import db
from datetime import timedelta

auth_bp = Blueprint("auth_bp", __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Register a new user
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data.get("email")).first():
        return {"message": "Email already registered"}, 400

    # Create new user
    user = User(
        full_name=data.get("full_name"),
        email=data.get("email"),
        role=data.get("role", "traveler")  
    )
    user.password = data.get("password")  

    db.session.add(user)
    db.session.commit()

    return user_schema.dump(user), 201

# Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not user.check_password(data.get("password")):
        return {"message": "Invalid email or password"}, 401

    # Create JWT access token
    additional_claims = {"role": user.role}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims, expires_delta=timedelta(days=1))

    return {
        "access_token": access_token,
        "user": user_schema.dump(user)
    }, 200

# Logout
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Successfully logged out"})
    unset_jwt_cookies(response)
    return response, 200

# Get current logged-in user
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        return {"message": "User not found"}, 404
    return user_schema.dump(user), 200
