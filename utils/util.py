import jwt
import datetime
from flask import current_app, request, jsonify
from functools import wraps
from models import User  # Assuming User model is defined somewhere

# Function to generate JWT token
def encode_token(user_id):
    """
    Generate JWT token with user_id and expiration time.
    """
    try:
        # Payload contains user ID and expiration time (1 day from now)
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),  # Token expires in 1 day
            'iat': datetime.datetime.utcnow(),  # Issued at time
            'sub': user_id  # Subject (user ID)
        }
        # Generate JWT token using the secret key
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    except Exception as e:
        return str(e)

# Function to decode and verify JWT token
def decode_token(token):
    """
    Decode the JWT token to extract the user ID.
    """
    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']  # Return the user ID
    except jwt.ExpiredSignatureError:
        return 'Token expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

# Role-based access control decorator
def role_required(role):
    """
    Decorator to check if the user has the required role (e.g., 'admin' or 'user').
    """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract the token from the Authorization header
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Token is missing'}), 403
            
            # The token should be in the format "Bearer <token>", so we split to get the token part
            try:
                token = token.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 403

            # Decode the token to extract the user ID
            user_id = decode_token(token)
            if isinstance(user_id, str):  # Token is invalid or expired
                return jsonify({'message': user_id}), 403

            # Fetch the user from the database using the decoded user ID
            user = User.query.get(user_id)
            if not user or user.role != role:
                return jsonify({'message': f'Access denied. {role} role required.'}), 403
            
            # If the user has the required role, proceed with the request
            return f(*args, **kwargs)
        return decorated_function
    return wrapper
