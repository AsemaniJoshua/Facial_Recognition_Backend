from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__, url_prefix='/api/v1')

@health_bp.route('/health', methods=['GET'])
def health_check():
    # You can add more checks here (DB, external services, etc.)
    return jsonify({
        'status': 'ok',
        'message': 'Service healthy',
        'uptime': 'TODO',  # Optionally add uptime tracking
    }), 200
