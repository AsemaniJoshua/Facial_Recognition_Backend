from flask import Blueprint, request, jsonify
import requests, os
from Blueprint_app.models import db, User
from Blueprint_app.middleware import verify_credentials

intlpay_bp = Blueprint('intlpay', __name__, url_prefix='/api/v1/payment/intl')

# Initiate international payment (e.g., Stripe)
@intlpay_bp.route('/initiate', methods=['POST'])
def initiate_intl():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    plan = data.get('plan')
    email = data.get('email', user.email)
    plan_prices = {'basic': 20, 'pro': 50, 'premium': 100}  # USD
    if plan not in plan_prices:
        return jsonify({'error': 'Invalid plan.'}), 400
    amount = plan_prices[plan]
    # Example: Stripe payment intent
    headers = {
        'Authorization': f'Bearer {os.getenv("STRIPE_SECRET")}'
    }
    payload = {
        'amount': int(amount * 100),
        'currency': 'usd',
        'metadata': {'user_id': user.id, 'plan': plan},
        'receipt_email': email
    }
    resp = requests.post('https://api.stripe.com/v1/payment_intents', data=payload, headers=headers)
    if resp.status_code == 200:
        return jsonify(resp.json()), 200
    return jsonify({'error': 'Failed to initiate payment.'}), 500

# Stripe webhook
@intlpay_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    event = request.json.get('type')
    data = request.json.get('data', {}).get('object', {})
    metadata = data.get('metadata', {})
    user_id = metadata.get('user_id')
    plan = metadata.get('plan')
    if event == 'payment_intent.succeeded' and user_id and plan:
        user = User.query.get(user_id)
        if user:
            user.payment_plan = plan
            user.payment_active = True
            db.session.commit()
    return '', 200
