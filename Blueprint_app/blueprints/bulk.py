from flask import Blueprint, request, jsonify, g
from Blueprint_app.models import db, Person, PersonAttendance
from Blueprint_app.middleware import verify_credentials, request_limit
from datetime import datetime
import base64
import face_recognition
import pickle
import io

bulk_bp = Blueprint('bulk', __name__, url_prefix='/api/v1/bulk')

@bulk_bp.route('/person/register', methods=['POST'])
def bulk_register_person():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    persons = data.get('persons')
    if not persons or not isinstance(persons, list):
        return jsonify({'error': 'Missing or invalid persons list.'}), 400
    results = []
    for p in persons:
        image_b64 = p.get('image')
        first_name = p.get('first_name')
        middle_name = p.get('middle_name')
        last_name = p.get('last_name')
        age = p.get('age')
        if not all([image_b64, first_name, last_name, age]):
            results.append({'error': 'Missing required fields.'})
            continue
        try:
            if ',' in image_b64:
                image_b64 = image_b64.split(',')[1]
            image_bytes = base64.b64decode(image_b64)
            image = face_recognition.load_image_file(io.BytesIO(image_bytes))
            face_locations = face_recognition.face_locations(image)
            encodings = face_recognition.face_encodings(image, face_locations)
            if not encodings:
                results.append({'error': 'No faces found.'})
                continue
            encoding = pickle.dumps(encodings[0])
            person = Person(
                user_id=user.id,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                age=age,
                face_encoding=encoding
            )
            db.session.add(person)
            db.session.commit()
            results.append({'message': 'Person registered.', 'person_id': person.id})
        except Exception as e:
            results.append({'error': str(e)})
    return jsonify({'results': results}), 200

@bulk_bp.route('/person/attendance', methods=['POST'])
def bulk_mark_person_attendance():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    images = data.get('images')
    if not images or not isinstance(images, list):
        return jsonify({'error': 'Missing or invalid images list.'}), 400
    results = []
    persons = Person.query.filter_by(user_id=user.id).all()
    known_encodings = [pickle.loads(p.face_encoding) for p in persons]
    person_ids = [p.id for p in persons]
    tolerance = getattr(user, 'face_tolerance', 0.6)
    from Blueprint_app.utils_notification import send_notification
    for image_b64 in images:
        try:
            if ',' in image_b64:
                image_b64 = image_b64.split(',')[1]
            image_bytes = base64.b64decode(image_b64)
            image = face_recognition.load_image_file(io.BytesIO(image_bytes))
            face_locations = face_recognition.face_locations(image)
            encodings = face_recognition.face_encodings(image, face_locations)
            if not encodings:
                results.append({'error': 'No faces found.'})
                continue
            found_id = None
            for unknown_encoding in encodings:
                matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=tolerance)
                if True in matches:
                    found_id = person_ids[matches.index(True)]
                    break
            if not found_id:
                results.append({'error': 'No matching person found.'})
                continue
            today = datetime.utcnow().date()
            existing = PersonAttendance.query.filter_by(person_id=found_id, user_id=user.id).filter(PersonAttendance.timestamp >= today).first()
            if existing:
                results.append({'error': 'Attendance already marked for today.'})
                continue
            attendance = PersonAttendance(person_id=found_id, user_id=user.id, timestamp=datetime.utcnow())
            db.session.add(attendance)
            db.session.commit()
            send_notification(user.id, 'Bulk Attendance Marked', f'Attendance marked for person ID {found_id}.')
            results.append({'message': 'Attendance marked.', 'person_id': found_id})
        except Exception as e:
            results.append({'error': str(e)})
    return jsonify({'results': results}), 200
