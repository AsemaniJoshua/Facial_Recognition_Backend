from flask import Blueprint, request, jsonify
import requests, os
from Blueprint_app.models import db, User
from Blueprint_app.middleware import verify_credentials

paystack_bp = Blueprint('paystack', __name__, url_prefix='/api/v1/payment/paystack')

# Initiate Paystack payment
@paystack_bp.route('/initiate', methods=['POST'])
def initiate_paystack():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    plan = data.get('plan')
    email = data.get('email', user.email)
    # Prices in Ghana Cedis (GHS)
    plan_prices = {'basic': 240, 'pro': 600, 'premium': 1200}  # GHS
    if plan not in plan_prices:
        return jsonify({'error': 'Invalid plan.'}), 400
    amount = plan_prices[plan] * 100  # Paystack expects pesewas (GHS * 100)
    headers = {
        'Authorization': f'Bearer {os.getenv("PAYSTACK_SECRET")}'
    }
    payload = {
        'email': email,
        'amount': amount,
        'currency': 'GHS',
        'metadata': {'user_id': user.id, 'plan': plan}
    }
    resp = requests.post('https://api.paystack.co/transaction/initialize', json=payload, headers=headers)
    if resp.status_code == 200:
        return jsonify(resp.json()), 200
    return jsonify({'error': 'Failed to initiate payment.'}), 500

# Paystack webhook
@paystack_bp.route('/webhook', methods=['POST'])
def paystack_webhook():
    event = request.json.get('event')
    data = request.json.get('data', {})
    metadata = data.get('metadata', {})
    user_id = metadata.get('user_id')
    plan = metadata.get('plan')
    if event == 'charge.success' and user_id and plan:
        user = User.query.get(user_id)
        if user:
            user.payment_plan = plan
            user.payment_active = True
            db.session.commit()
    return '', 200
