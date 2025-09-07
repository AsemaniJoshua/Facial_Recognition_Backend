import pickle
import face_recognition
from flask import Blueprint, request, jsonify, current_app
from ...app import db
from ...models import Student
import logging
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# Initialize the Blueprint
core = Blueprint('core', __name__, url_prefix='/api')

@core.route('/register', methods=['POST'])
def register_student():
    """
    Registers a new student with a single profile image for face encoding.
    Expects 'profileImage' in request.files.
    """
    if 'profileImage' not in request.files:
        return jsonify({"success": False, "message": "No profile image provided"}), 400

    image_file = request.files['profileImage']
    
    # Save the profile image
    filename = secure_filename(image_file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    image_path = os.path.join(upload_folder, filename)
    image_file.save(image_path)
    
    # Reset file pointer to the beginning for face recognition processing
    image_file.seek(0)


    profile_image_url = f"/uploads/{filename}"

    data = request.form
    student_id = data.get('studentId')
    full_name = data.get('fullName')
    email = data.get('email')
    class_name = data.get('className')

    if not all([student_id, full_name, email, class_name]):
        return jsonify({"success": False, "message": "Missing form data"}), 400

    if Student.query.filter((Student.id == student_id) | (Student.email == email)).first():
        return jsonify({"success": False, "message": "Student with this ID or email already exists"}), 409

    try:
        image = face_recognition.load_image_file(image_file)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return jsonify({"success": False, "message": "No face found in the image. Please retake."}), 400
        
        # Use the first encoding found
        face_encoding = face_encodings[0]
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing image: {e}"}), 500

    # Serialize the single encoding
    serialized_encoding = pickle.dumps(face_encoding)

    new_student = Student(
        id=student_id,
        fullName=full_name,
        email=email,
        class_name=class_name,
        face_encoding=serialized_encoding,
        profile_image_url=profile_image_url,
        last_seen=datetime.utcnow()
    )

    # Set a default password for the student. The password_hash field cannot be null.
    # Using the student's ID is a sensible default.
    new_student.set_password(student_id)

    try:
        db.session.add(new_student)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Student registered successfully!",
            "student": {
                "id": new_student.id,
                "fullName": new_student.fullName,
                "email": new_student.email,
                "class": new_student.class_name,
                "profile_image_url": new_student.profile_image_url
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        # Log the specific database error for easier debugging
        logging.error(f"Database error during registration: {e}")
        return jsonify({"success": False, "message": "A database error occurred during registration."}), 500