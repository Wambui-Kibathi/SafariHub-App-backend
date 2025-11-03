from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify, request

def role_required(roles):
    """
    Decorator to require specific user roles.
    `roles` can be a string (single role) or list of roles.
    """
    if isinstance(roles, str):
        roles = [roles]

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Handle OPTIONS requests for CORS
            if request.method == 'OPTIONS':
                return '', 200
            
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in roles:
                return jsonify({"message": "Unauthorized"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator