from flask import Blueprint, request, jsonify, g
from Blueprint_app.models import db, Person, PersonAttendance
from Blueprint_app.middleware import verify_credentials, request_limit
from datetime import datetime
import base64
import face_recognition
import pickle
import io

person_bp = Blueprint('person', __name__, url_prefix='/api/v1/person')

@person_bp.route('/register', methods=['POST'])
def register_person():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    image_b64 = data.get('image')
    first_name = data.get('first_name')
    middle_name = data.get('middle_name')
    last_name = data.get('last_name')
    age = data.get('age')
    if not all([image_b64, first_name, last_name, age]):
        return jsonify({'error': 'Missing required fields.'}), 400
    if ',' in image_b64:
        image_b64 = image_b64.split(',')[1]
    image_bytes = base64.b64decode(image_b64)
    image = face_recognition.load_image_file(io.BytesIO(image_bytes))
    face_locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, face_locations)
    if not encodings:
        return jsonify({'error': 'No faces found.'}), 404
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
    return jsonify({'message': 'Person registered successfully.', 'person_id': person.id}), 201

@person_bp.route('/attendance', methods=['POST'])
def mark_person_attendance():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    data = request.get_json()
    image_b64 = data.get('image')
    if not image_b64:
        return jsonify({'error': 'No image provided.'}), 400
    if ',' in image_b64:
        image_b64 = image_b64.split(',')[1]
    image_bytes = base64.b64decode(image_b64)
    image = face_recognition.load_image_file(io.BytesIO(image_bytes))
    face_locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, face_locations)
    if not encodings:
        from Blueprint_app.utils import log_audit
        response = {'error': 'No faces found.'}
        log_audit('/api/v1/person/attendance', 'POST', request.get_json(), response, 404)
        return jsonify(response), 404
    # Find matching person for this dev
    persons = Person.query.filter_by(user_id=user.id).all()
    known_encodings = [pickle.loads(p.face_encoding) for p in persons]
    person_ids = [p.id for p in persons]
    found_id = None
    tolerance = getattr(user, 'face_tolerance', 0.6)
    for unknown_encoding in encodings:
        matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=tolerance)
        if True in matches:
            found_id = person_ids[matches.index(True)]
            break
    if not found_id:
        from Blueprint_app.utils import log_audit
        response = {'error': 'No matching person found.'}
        log_audit('/api/v1/person/attendance', 'POST', request.get_json(), response, 404)
        return jsonify(response), 404
    today = datetime.utcnow().date()
    existing = PersonAttendance.query.filter_by(person_id=found_id, user_id=user.id).filter(PersonAttendance.timestamp >= today).first()
    if existing:
        from Blueprint_app.utils import log_audit
        response = {'error': 'Attendance already marked for today.'}
        log_audit('/api/v1/person/attendance', 'POST', request.get_json(), response, 409)
        return jsonify(response), 409
    attendance = PersonAttendance(person_id=found_id, user_id=user.id, timestamp=datetime.utcnow())
    db.session.add(attendance)
    db.session.commit()

    # Trigger webhooks for face recognition event
    from Blueprint_app.utils import trigger_webhooks, log_audit
    payload = {
        'user_id': user.id,
        'person_id': found_id,
        'timestamp': attendance.timestamp.isoformat(),
        'event': 'face_recognition',
    }
    trigger_webhooks(user.id, 'face_recognition', payload)

    response = {'message': 'Attendance marked successfully.', 'person_id': found_id}
    log_audit('/api/v1/person/attendance', 'POST', request.get_json(), response, 200)
    return jsonify(response), 200
