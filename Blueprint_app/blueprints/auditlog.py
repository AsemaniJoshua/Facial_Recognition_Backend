from flask import Blueprint, jsonify, g
from Blueprint_app.models import AuditLog
from Blueprint_app.middleware import verify_credentials

auditlog_bp = Blueprint('auditlog', __name__, url_prefix='/api/v1/auditlog')

@auditlog_bp.route('/list', methods=['GET'])
def list_audit_logs():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    logs = AuditLog.query.filter_by(user_id=user.id).order_by(AuditLog.timestamp.desc()).limit(100).all()
    result = [
        {
            'id': log.id,
            'timestamp': log.timestamp.isoformat(),
            'endpoint': log.endpoint,
            'method': log.method,
            'request_data': log.request_data,
            'response_data': log.response_data,
            'status_code': log.status_code
        }
        for log in logs
    ]
    return jsonify({'audit_logs': result}), 200
