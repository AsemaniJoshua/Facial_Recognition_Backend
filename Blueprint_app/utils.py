from Blueprint_app.models import AuditLog
from flask import request, g

def log_audit(endpoint, method, request_data, response_data, status_code):
    user = getattr(g, 'current_user', None)
    if not user:
        return
    log = AuditLog(
        user_id=user.id,
        endpoint=endpoint,
        method=method,
        request_data=str(request_data),
        response_data=str(response_data),
        status_code=status_code
    )
    from Blueprint_app.models import db
    db.session.add(log)
    db.session.commit()
import requests
from Blueprint_app.models import Webhook

def trigger_webhooks(user_id, event, payload):
    webhooks = Webhook.query.filter_by(user_id=user_id, event=event).all()
    for webhook in webhooks:
        try:
            resp = requests.post(webhook.url, json=payload, timeout=5)
            # Optionally log resp.status_code, resp.text
        except Exception as e:
            # Optionally log error and implement retry logic
            pass
