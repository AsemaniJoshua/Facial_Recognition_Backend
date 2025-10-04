from flask import Blueprint, request, jsonify, g
from Blueprint_app.models import db, User
from Blueprint_app.middleware import verify_credentials

payment_bp = Blueprint('payment', __name__, url_prefix='/api/v1/payment')

# Get current plan
@payment_bp.route('/plan', methods=['GET'])
def get_plan():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    return jsonify({
        'plan': user.payment_plan,
        'active': user.payment_active
    }), 200

# Update plan after successful payment (called by webhook or callback)
@payment_bp.route('/activate', methods=['POST'])
def activate_plan():
    data = request.get_json()
    user_id = data.get('user_id')
    plan = data.get('plan')
    if plan not in ['basic', 'pro', 'premium']:
        return jsonify({'error': 'Invalid plan.'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    user.payment_plan = plan
    user.payment_active = True
    db.session.commit()
    return jsonify({'message': 'Payment plan activated.', 'plan': plan}), 200

# Deactivate plan (e.g. on failed payment)
@payment_bp.route('/deactivate', methods=['POST'])
def deactivate_plan():
    data = request.get_json()
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    user.payment_plan = 'free'
    user.payment_active = False
    db.session.commit()
    return jsonify({'message': 'Payment plan deactivated.'}), 200
