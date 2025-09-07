from flask import Blueprint, jsonify
from ...app import db
from ...models import Student

# Initialize the Blueprint
students = Blueprint('students', __name__)

def student_to_dict(student):
    """Converts a Student object to a dictionary."""
    return {
        "id": student.id,
        "fullName": student.fullName,
        "email": student.email,
        "class": student.class_name,
        "status": student.status,
        "attendance_percent": student.attendance_percent,
        "last_seen": student.last_seen.isoformat() if student.last_seen else None,
        "profileImage": student.profile_image_url
    }

@students.route('/students', methods=['GET'])
def get_all_students():
    """
    Gets all registered students.
    """
    try:
        all_students = Student.query.all()
        return jsonify({
            "success": True,
            "students": [student_to_dict(s) for s in all_students]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@students.route('/student/<string:id>', methods=['GET'])
def get_student_by_id(id):
    """
    Gets a student by their ID.
    """
    try:
        student = Student.query.get(id)
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404
        return jsonify({"success": True, "student": student_to_dict(student)}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@students.route('/student/fullname/<path:fullname>', methods=['GET'])
def get_student_by_fullname(fullname):
    """
    Gets students by their full name (case-insensitive, partial match).
    """
    try:
        student_list = Student.query.filter(Student.fullName.ilike(f"%{fullname}%")).all()
        if not student_list:
            return jsonify({"success": False, "message": "No students found with that name"}), 404
        return jsonify({
            "success": True,
            "students": [student_to_dict(s) for s in student_list]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@students.route('/student/email/<string:email>', methods=['GET'])
def get_student_by_email(email):
    """
    Gets a student by their email.
    """
    try:
        student = Student.query.filter_by(email=email).first()
        if not student:
            return jsonify({"success": False, "message": "Student not found with that email"}), 404
        return jsonify({"success": True, "student": student_to_dict(student)}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

