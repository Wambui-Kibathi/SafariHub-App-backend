from flask_jwt_extended import create_access_token, get_jwt_identity
from datetime import timedelta

def create_token(user_id, role, expires_days=1):
    """Create a JWT with user ID and role"""
    from flask_jwt_extended import create_access_token
    additional_claims = {"role": role}
    token = create_access_token(identity=user_id, additional_claims=additional_claims, expires_delta=timedelta(days=expires_days))
    return token

def get_current_user_id():
    """Return the current user ID from JWT"""
    from flask_jwt_extended import get_jwt_identity
    return get_jwt_identity()