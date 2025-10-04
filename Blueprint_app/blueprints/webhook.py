from flask import Blueprint, request, jsonify, g
from Blueprint_app.models import db, Webhook
from Blueprint_app.middleware import verify_credentials

webhook_bp = Blueprint('webhook', __name__, url_prefix='/api/v1/webhook')

# Register a webhook
@webhook_bp.route('/register', methods=['POST'])
def register_webhook():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    url = data.get('url')
    event = data.get('event')
    if not url or not event:
        return jsonify({'error': 'Missing url or event.'}), 400
    webhook = Webhook(user_id=user.id, url=url, event=event)
    db.session.add(webhook)
    db.session.commit()
    return jsonify({'message': 'Webhook registered.', 'webhook_id': webhook.id}), 201

# List webhooks
@webhook_bp.route('/list', methods=['GET'])
def list_webhooks():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    webhooks = Webhook.query.filter_by(user_id=user.id).all()
    result = [{'id': w.id, 'url': w.url, 'event': w.event} for w in webhooks]
    return jsonify({'webhooks': result}), 200

# Delete a webhook
@webhook_bp.route('/delete/<int:webhook_id>', methods=['DELETE'])
def delete_webhook(webhook_id):
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=user.id).first()
    if not webhook:
        return jsonify({'error': 'Webhook not found.'}), 404
    db.session.delete(webhook)
    db.session.commit()
    return jsonify({'message': 'Webhook deleted.'}), 200

# Update a webhook
@webhook_bp.route('/update/<int:webhook_id>', methods=['PUT'])
def update_webhook(webhook_id):
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=user.id).first()
    if not webhook:
        return jsonify({'error': 'Webhook not found.'}), 404
    data = request.get_json()
    url = data.get('url')
    event = data.get('event')
    if url:
        webhook.url = url
    if event:
        webhook.event = event
    db.session.commit()
    return jsonify({'message': 'Webhook updated.'}), 200
