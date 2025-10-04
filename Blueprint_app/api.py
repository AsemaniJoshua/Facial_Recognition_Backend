from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from Blueprint_app.models import db, User, Attendance, TestFaceEncoding
from Blueprint_app.middleware import verify_credentials, request_limit
from datetime import datetime, timedelta
import secrets
import base64
import face_recognition
import pickle
import os
import io

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
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
        last_request_date=datetime.utcnow().date()
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'message': 'Registration successful.',
        'credentials': {
            'api_key': api_key,
            'api_secret': api_secret,
            'token_access': token_access,
            'token_access_secret': token_access_secret
        }
    }), 201

@api.route('/attendance', methods=['POST'])
def mark_attendance():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error

    # ...existing imports...
    from flask import Blueprint, request, jsonify, g
    from werkzeug.security import generate_password_hash, check_password_hash
    from Blueprint_app.models import db, User, Attendance, TestingFaceEncoding
    from Blueprint_app.middleware import verify_credentials, request_limit
    from datetime import datetime
    import secrets
    import base64
    import face_recognition
    import pickle
    import io

    api = Blueprint('api', __name__, url_prefix='/api/v1')

    # User registration endpoint
    @api.route('/signup', methods=['POST'])
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

    # User login endpoint
    @api.route('/login', methods=['POST'])
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

    # Extract face encodings from image
    @api.route('/face/extract', methods=['POST'])
    def extract_face():
        cred_error = verify_credentials()
        if cred_error:
            return cred_error
        data = request.get_json()
        image_b64 = data.get('image')
        if not image_b64:
            return jsonify({'error': 'No image provided.'}), 400
        if ',' in image_b64:
            image_b64 = image_b64.split(',')[1]
        image_bytes = base64.b64decode(image_b64)
        unknown_image = face_recognition.load_image_file(io.BytesIO(image_bytes))
        face_locations = face_recognition.face_locations(unknown_image)
        encodings = face_recognition.face_encodings(unknown_image, face_locations)
        if not encodings:
            return jsonify({'error': 'No faces found.'}), 404
        # Return encodings as base64 strings
        encoding_list = [base64.b64encode(pickle.dumps(e)).decode('utf-8') for e in encodings]
        return jsonify({'encodings': encoding_list}), 200

    # Mark attendance (once per 24h per user)
    @api.route('/attendance/mark', methods=['POST'])
    def mark_attendance():
        cred_error = verify_credentials()
        if cred_error:
            return cred_error
        limit_error = request_limit('attendance')
        if limit_error:
            return limit_error
        user = g.current_user
        today = datetime.utcnow().date()
        existing = Attendance.query.filter_by(user_id=user.id, timestamp=today).first()
        if existing:
            return jsonify({'error': 'Attendance already marked for today.'}), 409
        attendance = Attendance(user_id=user.id, timestamp=datetime.utcnow())
        db.session.add(attendance)
        db.session.commit()
        return jsonify({'message': 'Attendance marked.'}), 200

    # Upload image for testing (store encoding temporarily)
    @api.route('/testing/upload', methods=['POST'])
    def upload_testing():
        cred_error = verify_credentials()
        if cred_error:
            return cred_error
        limit_error = request_limit('testing')
        if limit_error:
            return limit_error
        user = g.current_user
        data = request.get_json()
        image_b64 = data.get('image')
        if not image_b64:
            return jsonify({'error': 'No image provided.'}), 400
        if ',' in image_b64:
            image_b64 = image_b64.split(',')[1]
        image_bytes = base64.b64decode(image_b64)
        unknown_image = face_recognition.load_image_file(io.BytesIO(image_bytes))
        face_locations = face_recognition.face_locations(unknown_image)
        encodings = face_recognition.face_encodings(unknown_image, face_locations)
        if not encodings:
            return jsonify({'error': 'No faces found.'}), 404
        for encoding in encodings:
            db.session.add(TestingFaceEncoding(user_id=user.id, encoding=pickle.dumps(encoding)))
        db.session.commit()
        return jsonify({'message': 'Test face encoding(s) stored.'}), 201

    # Check if test encoding exists for user
    @api.route('/testing/check', methods=['POST'])
    def check_testing():
        cred_error = verify_credentials()
        if cred_error:
            return cred_error
        user = g.current_user
        data = request.get_json()
        image_b64 = data.get('image')
        if not image_b64:
            return jsonify({'error': 'No image provided.'}), 400
        if ',' in image_b64:
            image_b64 = image_b64.split(',')[1]
        image_bytes = base64.b64decode(image_b64)
        unknown_image = face_recognition.load_image_file(io.BytesIO(image_bytes))
        face_locations = face_recognition.face_locations(unknown_image)
        encodings = face_recognition.face_encodings(unknown_image, face_locations)
        if not encodings:
            return jsonify({'error': 'No faces found.'}), 404
        test_encodings = TestingFaceEncoding.query.filter_by(user_id=user.id).all()
        known_encodings = [pickle.loads(te.encoding) for te in test_encodings]
        found = False
        for unknown_encoding in encodings:
            matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=0.6)
            if True in matches:
                found = True
                break
        return jsonify({'exists': found}), 200

    # Analytics: Get user info
    @api.route('/analytics/user', methods=['GET'])
    def get_user_info():
        cred_error = verify_credentials()
        if cred_error:
            return cred_error
        user = g.current_user
        info = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'age': user.age
        }
        return jsonify({'user_info': info}), 200

    # Analytics: Get total attendance for user
    @api.route('/analytics/attendance-count', methods=['GET'])
    def get_attendance_count():
        cred_error = verify_credentials()
        if cred_error:
            return cred_error
        user = g.current_user
        count = Attendance.query.filter_by(user_id=user.id).count()
        return jsonify({'attendance_count': count}), 200
