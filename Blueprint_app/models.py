from Blueprint_app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    endpoint = db.Column(db.String(128), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    request_data = db.Column(db.Text)
    response_data = db.Column(db.Text)
    status_code = db.Column(db.Integer)
class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    event = db.Column(db.String(64), nullable=False)  # e.g. 'attendance', 'face_recognition'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64), nullable=False)
    age = db.Column(db.Integer)
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PersonAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    payment_plan = db.Column(db.String(20), default='free')  # free, basic, pro, premium
    payment_active = db.Column(db.Boolean, default=False)
    notifications_enabled = db.Column(db.Boolean, default=True)
    notification_email = db.Column(db.String(120))
    attendance_retention_days = db.Column(db.Integer, default=365)
    face_data_retention_days = db.Column(db.Integer, default=365)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    api_secret = db.Column(db.String(64), nullable=False)
    token_access = db.Column(db.String(64), nullable=False)
    token_access_secret = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    age = db.Column(db.Integer)
    attendance_requests_today = db.Column(db.Integer, default=0)
    testing_requests_today = db.Column(db.Integer, default=0)
    last_request_date = db.Column(db.Date, default=datetime.utcnow)
    face_tolerance = db.Column(db.Float, default=0.6)
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_email = db.Column(db.String(120))
    mfa_code = db.Column(db.String(8))
    mfa_code_expiry = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='present')

class TestingFaceEncoding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    encoding = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
