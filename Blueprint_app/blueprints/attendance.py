from flask import Blueprint, request, jsonify, g
from Blueprint_app.models import db, Attendance
from Blueprint_app.middleware import verify_credentials, request_limit
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/v1/attendance')

@attendance_bp.route('/mark', methods=['POST'])
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
        from Blueprint_app.utils import log_audit
        response = {'error': 'Attendance already marked for today.'}
        log_audit('/api/v1/attendance/mark', 'POST', request.get_json(), response, 409)
        return jsonify(response), 409
    attendance = Attendance(user_id=user.id, timestamp=datetime.utcnow())
    db.session.add(attendance)
    db.session.commit()

    # Trigger webhooks for attendance event
    from Blueprint_app.utils import trigger_webhooks, log_audit
    payload = {
        'user_id': user.id,
        'timestamp': attendance.timestamp.isoformat(),
        'event': 'attendance',
    }
    trigger_webhooks(user.id, 'attendance', payload)

    response = {'message': 'Attendance marked.'}
    log_audit('/api/v1/attendance/mark', 'POST', request.get_json(), response, 200)
    # Send notification if enabled
    from Blueprint_app.utils_notification import send_notification
    send_notification(user.id, 'Attendance Marked', 'Your attendance was marked successfully.')
    return jsonify(response), 200
