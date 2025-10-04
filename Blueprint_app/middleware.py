import time
from collections import defaultdict
from flask import request, jsonify, g
from Blueprint_app.models import User, db
from datetime import datetime

# In-memory stores (replace with Redis for production)
ip_request_times = defaultdict(list)
blocked_ips = set()

GLOBAL_RATE_LIMIT = 1000  # requests per hour per IP
RATE_LIMIT_WINDOW = 3600  # seconds
BLOCK_DURATION = 3600     # seconds
ip_blocked_until = {}

def global_rate_limit():
    ip = request.remote_addr
    now = time.time()
    # Unblock IP if block expired
    if ip in ip_blocked_until and now > ip_blocked_until[ip]:
        blocked_ips.discard(ip)
        del ip_blocked_until[ip]
    if ip in blocked_ips:
        return jsonify({'error': 'IP blocked due to abuse.'}), 403
    # Clean up old requests
    ip_request_times[ip] = [t for t in ip_request_times[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(ip_request_times[ip]) >= GLOBAL_RATE_LIMIT:
        blocked_ips.add(ip)
        ip_blocked_until[ip] = now + BLOCK_DURATION
        return jsonify({'error': 'Rate limit exceeded. IP temporarily blocked.'}), 429
    ip_request_times[ip].append(now)
    return None


def verify_credentials():
    api_key = request.headers.get('X-API-KEY')
    api_secret = request.headers.get('X-API-SECRET')
    token_access = request.headers.get('X-TOKEN-ACCESS')
    token_access_secret = request.headers.get('X-TOKEN-ACCESS-SECRET')

    if not all([api_key, api_secret, token_access, token_access_secret]):
        return jsonify({'error': 'Missing API credentials.', 'code': 'AUTH_MISSING'}), 401

    user = User.query.filter_by(
        api_key=api_key,
        api_secret=api_secret,
        token_access=token_access,
        token_access_secret=token_access_secret
    ).first()
    if not user:
        return jsonify({'error': 'Invalid API credentials.', 'code': 'AUTH_INVALID'}), 401
    g.current_user = user
    return None

def request_limit(endpoint_type):
    user = getattr(g, 'current_user', None)
    if not user:
        return jsonify({'error': 'User not found for request limit.', 'code': 'USER_NOT_FOUND'}), 401
    today = datetime.utcnow().date()
    if user.last_request_date != today:
        user.attendance_requests_today = 0
        user.testing_requests_today = 0
        user.last_request_date = today
    # Set limits based on payment plan
    plan_limits = {
        'free': 10,
        'basic': 100,
        'pro': 500,
        'premium': 1500
    }
    limit = plan_limits.get(getattr(user, 'payment_plan', 'free'), 10)
    if not getattr(user, 'payment_active', False):
        limit = 10  # fallback to free if payment not active
    if endpoint_type == 'attendance':
        if user.attendance_requests_today >= limit:
            return jsonify({'error': 'Attendance request limit reached for today.', 'code': 'RATE_LIMIT_ATTENDANCE'}), 429
        user.attendance_requests_today += 1
    elif endpoint_type == 'testing':
        if user.testing_requests_today >= limit:
            return jsonify({'error': 'Testing request limit reached for today.', 'code': 'RATE_LIMIT_TESTING'}), 429
        user.testing_requests_today += 1
    db.session.commit()
    return None
