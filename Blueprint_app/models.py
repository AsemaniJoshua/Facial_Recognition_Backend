from .app import db, bcrypt
from datetime import datetime
from flask_login import UserMixin
import pickle

class Student(db.Model, UserMixin):
    id = db.Column(db.String(50), primary_key=True)
    fullName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    attendance_percent = db.Column(db.Integer)
    status = db.Column(db.String(20))
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image_url = db.Column(db.String(200))
    face_encoding = db.Column(db.LargeBinary, nullable=True)
    password_hash = db.Column(db.String(60), nullable=False) # Store the hashed password

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class AttendanceRecord(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    student_id = db.Column(db.String(50), db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    time = db.Column(db.Time)
    
    student = db.relationship('Student', backref=db.backref('attendanceRecords', lazy=True))

class DashboardMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))

class Chart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    present = db.Column(db.Integer, nullable=False)
    absent = db.Column(db.Integer, nullable=False)

class AttendanceMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer, nullable=False)
