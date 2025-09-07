import base64
import face_recognition
import numpy as np
import pickle
from flask import Blueprint, request, jsonify
from datetime import datetime
from ...app import db, bcrypt
from ...models import Student, AttendanceRecord
import uuid
import os
from werkzeug.utils import secure_filename
import io

# Initialize the Blueprint
attendance = Blueprint('attendance', __name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def attendance_to_dict(record):
    """Converts an AttendanceRecord object to a dictionary."""
    return {
        'id': record.id,
        'student_id': record.student_id,
        'date': record.date.isoformat(),
        'time': record.time.strftime("%H:%M:%S"),
        'status': record.status
    }

@attendance.route('/attendance', methods=['POST'])
def take_attendance():
    """
    Takes attendance by recognizing faces in an uploaded image.
    """
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"success": False, "error": "No image provided"}), 400

    profile_image_base64 = data['image']
    
    try:
        # Load all students and their face encodings from the database
        all_students = Student.query.all()
        known_face_encodings = []
        known_student_ids = []
        for s in all_students:
            if s.face_encoding:
                try:
                    known_face_encodings.append(pickle.loads(s.face_encoding))
                    known_student_ids.append(s.id)
                except pickle.UnpicklingError:
                    print(f"Error unpickling face encoding for student {s.id}")
        
        if not known_face_encodings:
            return jsonify({"success": False, "message": "No registered students with face data found"}), 404

        # Decode the base64 image
        if ',' in profile_image_base64:
            profile_image_base64 = profile_image_base64.split(',')[1]
        image_bytes = base64.b64decode(profile_image_base64)
        unknown_image = face_recognition.load_image_file(io.BytesIO(image_bytes))
        
        face_locations = face_recognition.face_locations(unknown_image)
        unknown_face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

        if not unknown_face_encodings:
            return jsonify({"success": False, "message": "No faces found in the provided image."}), 404

        matched_students = []
        already_marked_students = []
        # Use a set to keep track of students already marked present in this request
        recognized_student_ids_this_request = set()

        for unknown_encoding in unknown_face_encodings:
            # Compare the unknown face with all known face encodings from all students
            matches = [bool(m) for m in face_recognition.compare_faces(known_face_encodings, unknown_encoding, tolerance=0.6)]
            
            if True in matches:
                first_match_index = matches.index(True)
                student_id = known_student_ids[first_match_index]
                
                # Continue if this student has already been matched in the current image
                if student_id in recognized_student_ids_this_request:
                    continue

                student = Student.query.get(student_id)
                
                if student:
                    # Update last_seen for the student
                    student.last_seen = datetime.utcnow()

                    # Check if attendance already recorded for today
                    today = datetime.now().date()
                    existing_record = AttendanceRecord.query.filter_by(student_id=student_id, date=today).first()

                    if existing_record:
                        already_marked_students.append(student.fullName)
                        recognized_student_ids_this_request.add(student_id)
                        continue

                    # Log attendance in the database
                    attendance_record = AttendanceRecord(
                        id=str(uuid.uuid4()),
                        student_id=student_id,
                        date=today,
                        status="present",
                        time=datetime.now().time()
                    )
                    db.session.add(attendance_record)
                    
                    matched_students.append({
                        "id": student.id,
                        "fullName": student.fullName,
                        "email": student.email,
                        "class": student.class_name,
                        "status": "present",
                        "time": attendance_record.time.strftime("%H:%M")
                    })
                    recognized_student_ids_this_request.add(student_id)

        if not matched_students:
            if already_marked_students:
                return jsonify({"success": False, "message": f"Attendance already marked for: {', '.join(already_marked_students)}"}), 409
            return jsonify({"success": False, "message": "No registered students were recognized."}), 404

        # Commit all attendance records at once
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Attendance recorded.",
            "matchedStudents": matched_students
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@attendance.route('/allattendance', methods=['GET'])
def get_all_attendance():
    """
    Gets all attendance records.
    """
    try:
        records = AttendanceRecord.query.all()
        return jsonify({
            "success": True,
            "attendance": [attendance_to_dict(record) for record in records]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@attendance.route('/attendance/<string:id>', methods=['GET'])
def get_attendance_by_id(id):
    """
    Gets an attendance record by its ID.
    """
    try:
        record = AttendanceRecord.query.get(id)
        if not record:
            return jsonify({"success": False, "message": "Attendance record not found"}), 404
        return jsonify({"success": True, "attendance": attendance_to_dict(record)}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@attendance.route('/attendance/student/<string:student_id>', methods=['GET'])
def get_attendance_by_student_id(student_id):
    """
    Gets all attendance records for a specific student.
    """
    try:
        records = AttendanceRecord.query.filter_by(student_id=student_id).all()
        if not records:
            return jsonify({"success": False, "message": "No attendance records found for this student"}), 404
        return jsonify({
            "success": True,
            "attendance": [attendance_to_dict(record) for record in records]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@attendance.route('/attendance/date/<string:date_str>', methods=['GET'])
def get_attendance_by_date(date_str):
    """
    Gets all attendance records for a specific date.
    Date format should be YYYY-MM-DD.
    """
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        records = AttendanceRecord.query.filter_by(date=attendance_date).all()
        if not records:
            return jsonify({"success": False, "message": f"No attendance records found for date {date_str}"}), 404
        return jsonify({
            "success": True,
            "attendance": [attendance_to_dict(record) for record in records]
        }), 200
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format. Please use YYYY-MM-DD."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@attendance.route('/attendance/status/<string:status>', methods=['GET'])
def get_attendance_by_status(status):
    """
    Gets all attendance records with a specific status.
    """
    if status.lower() not in ['present', 'absent', 'late']:
        return jsonify({"success": False, "message": "Invalid status. Use 'present', 'absent', or 'late'."}), 400
    try:
        records = AttendanceRecord.query.filter_by(status=status.lower()).all()
        if not records:
            return jsonify({"success": False, "message": f"No attendance records found with status '{status}'"}), 404
        return jsonify({
            "success": True,
            "attendance": [attendance_to_dict(record) for record in records]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@attendance.route('/attendance/time/<string:time_str>', methods=['GET'])
def get_attendance_by_time(time_str):
    """
    Gets all attendance records at a specific time.
    Time format should be HH:MM:SS or HH:MM.
    """
    try:
        try:
            attendance_time = datetime.strptime(time_str, '%H:%M:%S').time()
        except ValueError:
            attendance_time = datetime.strptime(time_str, '%H:%M').time()
            
        records = AttendanceRecord.query.filter_by(time=attendance_time).all()
        if not records:
            return jsonify({"success": False, "message": f"No attendance records found for time {time_str}"}), 404
        return jsonify({
            "success": True,
            "attendance": [attendance_to_dict(record) for record in records]
        }), 200
    except ValueError:
        return jsonify({"success": False, "message": "Invalid time format. Please use HH:MM:SS or HH:MM."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500