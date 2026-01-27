from flask import Blueprint, request, jsonify
from models.user import User
from app import db
import sys
sys.path.append("..")
from utils.validators import validate_email, validate_password
import jwt
import datetime
from config import config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate email
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    if User.query.filter_by(username=data.get('username', data['email'])).first():
        return jsonify({'error': 'Username already taken'}), 409
    
    # Create new user
    new_user = User(
        username=data.get('username', data['email'].split('@')[0]),
        email=data['email'],
        password=data['password']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': new_user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing credentials'}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.verify_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Update last login
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, config.SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout (client-side token removal)"""
    return jsonify({'message': 'Logged out successfully'}), 200