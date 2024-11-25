from flask import Blueprint, jsonify, request
from models import User
from utils.util import encode_token
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth_bp', __name__)

# Login route to authenticate users and generate JWT token
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate the user by username and password, and return a JWT token.
    """
    data = request.get_json()
    
    # Get username and password from the request data
    username = data.get('username')
    password = data.get('password')

    # Fetch user from the database
    user = User.query.filter_by(username=username).first()

    # Check if user exists and password is correct
    if user and user.check_password(password):
        # Generate JWT token
        token = encode_token(user.id)
        return jsonify({'message': 'Login successful', 'token': token}), 200
    else:
        # If authentication fails, return error
        return jsonify({'message': 'Invalid username or password'}), 401
