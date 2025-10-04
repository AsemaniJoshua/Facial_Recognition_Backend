


from Blueprint_app.models import db
import secrets
from flask import Blueprint, jsonify, g
from Blueprint_app.models import User, Person, Attendance, PersonAttendance
from Blueprint_app.middleware import verify_credentials

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

# Update notification preferences
@admin_bp.route('/notifications', methods=['POST'])
def update_notifications():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    enabled = data.get('enabled')
    email = data.get('email')
    if enabled is not None:
        user.notifications_enabled = bool(enabled)
    if email:
        user.notification_email = email
    db.session.commit()
    return jsonify({'message': 'Notification preferences updated.', 'enabled': user.notifications_enabled, 'email': user.notification_email}), 200

# Update data retention policies
@admin_bp.route('/retention', methods=['POST'])
def update_retention():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    attendance_days = data.get('attendance_retention_days')
    face_days = data.get('face_data_retention_days')
    try:
        if attendance_days is not None:
            attendance_days = int(attendance_days)
            if attendance_days < 1:
                return jsonify({'error': 'Attendance retention must be >= 1 day.'}), 400
            user.attendance_retention_days = attendance_days
        if face_days is not None:
            face_days = int(face_days)
            if face_days < 1:
                return jsonify({'error': 'Face data retention must be >= 1 day.'}), 400
            user.face_data_retention_days = face_days
        db.session.commit()
        return jsonify({'message': 'Retention policies updated.', 'attendance_retention_days': user.attendance_retention_days, 'face_data_retention_days': user.face_data_retention_days}), 200
    except Exception:
        return jsonify({'error': 'Invalid retention value.'}), 400

# Update face recognition tolerance
@admin_bp.route('/face-tolerance', methods=['POST'])
def update_face_tolerance():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    tolerance = data.get('tolerance')
    try:
        tolerance = float(tolerance)
        if not (0.3 <= tolerance <= 1.0):
            return jsonify({'error': 'Tolerance must be between 0.3 and 1.0.'}), 400
        user.face_tolerance = tolerance
        db.session.commit()
        return jsonify({'message': 'Face recognition tolerance updated.', 'tolerance': tolerance}), 200
    except Exception:
        return jsonify({'error': 'Invalid tolerance value.'}), 400

# Regenerate API credentials
@admin_bp.route('/credentials/regenerate', methods=['POST'])
def regenerate_credentials():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    user.api_key = secrets.token_hex(32)
    user.api_secret = secrets.token_hex(32)
    user.token_access = secrets.token_hex(32)
    user.token_access_secret = secrets.token_hex(32)
    db.session.commit()
    return jsonify({
        'message': 'API credentials regenerated.',
        'api_key': user.api_key,
        'api_secret': user.api_secret,
        'token_access': user.token_access,
        'token_access_secret': user.token_access_secret
    }), 200

# Revoke API credentials (disable access)
@admin_bp.route('/credentials/revoke', methods=['POST'])
def revoke_credentials():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    user.api_key = None
    user.api_secret = None
    user.token_access = None
    user.token_access_secret = None
    db.session.commit()
    return jsonify({'message': 'API credentials revoked.'}), 200

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    total_persons = Person.query.filter_by(user_id=user.id).count()
    total_attendance = Attendance.query.filter_by(user_id=user.id).count()
    total_person_attendance = PersonAttendance.query.filter_by(user_id=user.id).count()
    return jsonify({
        'total_persons': total_persons,
        'total_attendance': total_attendance,
        'total_person_attendance': total_person_attendance
    }), 200

@admin_bp.route('/credentials', methods=['GET'])
def get_credentials():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    return jsonify({
        'api_key': user.api_key,
        'api_secret': user.api_secret,
        'token_access': user.token_access,
        'token_access_secret': user.token_access_secret
    }), 200

@admin_bp.route('/user', methods=['GET'])
def get_user_info():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'age': user.age
    }), 200
