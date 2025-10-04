from flask import Blueprint, jsonify, g
from Blueprint_app.models import Attendance
from Blueprint_app.middleware import verify_credentials

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/v1/analytics')

@analytics_bp.route('/user', methods=['GET'])
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

@analytics_bp.route('/attendance-count', methods=['GET'])
def get_attendance_count():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    count = Attendance.query.filter_by(user_id=user.id).count()
    return jsonify({'attendance_count': count}), 200
