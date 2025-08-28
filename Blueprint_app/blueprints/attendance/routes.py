import base64
import face_recognition
import numpy as np
import pickle
from flask import Blueprint, request, jsonify
from datetime import datetime
from ...app import db, bcrypt
from ...models import Student, AttendanceRecord

# Initialize the Blueprint
attendance = Blueprint('attendance', __name__)

@attendance.route('/register', methods=['POST'])
def register_student():
    """
    Registers a new student by storing their facial encoding and data in the database.
    This also hashes their password using Bcrypt.
    """
    data = request.get_json()
    if not data or not all(key in data for key in ["fullName", "studentId", "profileImage", "password"]):
        return jsonify({"success": False, "error": "Missing required data"}), 400

    student_id = data['studentId']
    full_name = data['fullName']
    profile_image_base64 = data['profileImage']
    password = data['password']

    try:
        # Check if student already exists
        existing_student = Student.query.get(student_id)
        if existing_student:
            return jsonify({"success": False, "message": f"Student with ID '{student_id}' already exists."}), 409
            
        # Decode the base64 image
        image_bytes = base64.b64decode(profile_image_base64)
        image_np = np.frombuffer(image_bytes, np.uint8)
        image = face_recognition.load_image_file(image_np)

        # Get face encodings
        face_encodings = face_recognition.face_encodings(image)
        if not face_encodings:
            return jsonify({"success": False, "message": "No face found in the image."}), 400

        # Create a new student object and save to the database
        new_student = Student(
            id=student_id,
            fullName=full_name,
            email=data.get("email"),
            class_name=data.get("class"),
            status="active",
            face_encoding=pickle.dumps(face_encodings[0])
        )
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Student registered successfully.",
            "student": {
                "id": student_id,
                "fullName": full_name,
                "email": data.get("email"),
                "class": data.get("class"),
                "status": "active"
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

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
        # Load all face encodings from the database
        all_students = Student.query.all()
        known_face_encodings = [pickle.loads(s.face_encoding) for s in all_students if s.face_encoding]
        known_student_ids = [s.id for s in all_students if s.face_encoding]
        
        if not known_face_encodings:
            return jsonify({"success": False, "message": "No registered students found"}), 404

        # Decode the base64 image
        image_bytes = base64.b64decode(profile_image_base64)
        image_np = np.frombuffer(image_bytes, np.uint8)
        unknown_image = face_recognition.load_image_file(image_np)
        
        face_locations = face_recognition.face_locations(unknown_image)
        unknown_face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

        if not unknown_face_encodings:
            return jsonify({"success": False, "message": "No faces found in the provided image."}), 404

        matched_students = []

        for unknown_encoding in unknown_face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, unknown_encoding)
            
            if True in matches:
                first_match_index = matches.index(True)
                student_id = known_student_ids[first_match_index]
                student = Student.query.get(student_id)
                
                if student:
                    # Log attendance in the database
                    attendance_record = AttendanceRecord(
                        student_id=student_id,
                        date=datetime.now().date(),
                        status="present",
                        time=datetime.now().time()
                    )
                    db.session.add(attendance_record)
                    db.session.commit()
                    
                    matched_students.append({
                        "id": student.id,
                        "fullName": student.fullName,
                        "email": student.email,
                        "class": student.class_name,
                        "status": "present",
                        "time": attendance_record.time.strftime("%H:%M")
                    })

        if not matched_students:
            return jsonify({"success": False, "message": "No registered students were recognized."}), 404

        return jsonify({
            "success": True,
            "message": "Attendance recorded.",
            "matchedStudents": matched_students
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500