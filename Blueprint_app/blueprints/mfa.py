from flask import Blueprint, request, jsonify, g
from Blueprint_app.models import db, User
from Blueprint_app.middleware import verify_credentials
from datetime import datetime, timedelta
import secrets
import smtplib, os
from email.message import EmailMessage

mfa_bp = Blueprint('mfa', __name__, url_prefix='/api/v1/mfa')

# Setup MFA (set email)
@mfa_bp.route('/setup', methods=['POST'])
def setup_mfa():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email required.'}), 400
    user.mfa_email = email
    db.session.commit()
    return jsonify({'message': 'MFA email set.'}), 200

# Request MFA code (send email)
@mfa_bp.route('/request', methods=['POST'])
def request_mfa_code():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    if not user.mfa_email:
        return jsonify({'error': 'MFA email not set.'}), 400
    code = str(secrets.randbelow(1000000)).zfill(6)
    user.mfa_code = code
    user.mfa_code_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    # Send email (simple SMTP, configure as needed)
    msg = EmailMessage()
    msg.set_content(f'Your MFA code is: {code}')
    msg['Subject'] = 'Your MFA Code'
    msg['From'] = 'no-reply@example.com'
    msg['To'] = user.mfa_email
    try:
        # Replace 'smtp.example.com' and credentials with your real SMTP server details
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            sender_mail=os.getenv(EMAIL_USER, "")
            sender_pass=os.getenv(EMAIL_PASS, "")
            s.login(sender_mail, sender_pass)
            s.send_message(msg)
    except Exception as e:
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500
    return jsonify({'message': 'MFA code sent.'}), 200

# Verify MFA code
@mfa_bp.route('/verify', methods=['POST'])
def verify_mfa_code():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify({'error': 'Code required.'}), 400
    if not user.mfa_code or not user.mfa_code_expiry:
        return jsonify({'error': 'No code requested.'}), 400
    if datetime.utcnow() > user.mfa_code_expiry:
        return jsonify({'error': 'Code expired.'}), 400
    if code != user.mfa_code:
        return jsonify({'error': 'Invalid code.'}), 401
    user.mfa_enabled = True
    user.mfa_code = None
    user.mfa_code_expiry = None
    db.session.commit()
    return jsonify({'message': 'MFA verified and enabled.'}), 200
