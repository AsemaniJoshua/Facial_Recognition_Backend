from flask import Blueprint, jsonify, request
from ...models import db, Student
from ...app import bcrypt
import face_recognition
import pickle
import os
from werkzeug.utils import secure_filename

core = Blueprint('core', __name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@core.route('/')
def index():
    return jsonify({"success": True, "message": "Welcome to the Facial Recognition Backend"})

@core.route('/api/register', methods=['POST'])
def register_student():
    if 'profileImage' not in request.files:
        return jsonify({"success": False, "error": "No profile image provided"}), 400

    file = request.files['profileImage']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        student_id = request.form.get('studentId')
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        class_name = request.form.get('class')

        if not all([student_id, full_name, email, class_name]):
            return jsonify({"success": False, "error": "Missing required data"}), 400

        try:
            # Check if student already exists
            existing_student = Student.query.get(student_id)
            if existing_student:
                return jsonify({"success": False, "message": f"Student with ID '{student_id}' already exists."}), 409
                
            # Load the image for face recognition
            image = face_recognition.load_image_file(file_path)

            # Get face encodings
            face_encodings = face_recognition.face_encodings(image)
            if not face_encodings:
                return jsonify({"success": False, "message": "No face found in the image."}), 400

            # Create a new student object and save to the database
            new_student = Student(
                id=student_id,
                fullName=full_name,
                email=email,
                class_name=class_name,
                profile_image_url=file_path,
                face_encoding=pickle.dumps(face_encodings[0])
            )
            new_student.set_password('password') # Set a default password
            db.session.add(new_student)
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Student registered successfully.",
                "student": {
                    "id": student_id,
                    "fullName": full_name,
                    "email": email,
                    "class": class_name,
                    "profileImage": file_path
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

