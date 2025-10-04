from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from Blueprint_app.models import db, User
import secrets
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    age = data.get('age')
    if not email or not password:
        return jsonify({'error': 'Email and password required.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists.'}), 400
    api_key = secrets.token_hex(32)
    api_secret = secrets.token_hex(32)
    token_access = secrets.token_hex(32)
    token_access_secret = secrets.token_hex(32)
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        api_key=api_key,
        api_secret=api_secret,
        token_access=token_access,
        token_access_secret=token_access_secret,
        first_name=first_name,
        last_name=last_name,
        age=age,
        last_request_date=datetime.utcnow().date()
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'message': 'Signup successful.',
        'credentials': {
            'api_key': api_key,
            'api_secret': api_secret,
            'token_access': token_access,
            'token_access_secret': token_access_secret
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password.'}), 401
    return jsonify({
        'message': 'Login successful.',
        'credentials': {
            'api_key': user.api_key,
            'api_secret': user.api_secret,
            'token_access': user.token_access,
            'token_access_secret': user.token_access_secret
        }
    }), 200
