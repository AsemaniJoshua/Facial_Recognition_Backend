from flask import Blueprint, request, jsonify, g
from Blueprint_app.models import db, TestingFaceEncoding
from Blueprint_app.middleware import verify_credentials, request_limit
import base64
import face_recognition
import pickle
import io


testing_bp = Blueprint('testing', __name__, url_prefix='/api/v1/testing')

@testing_bp.route('/upload', methods=['POST'])
def upload_testing():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    limit_error = request_limit('testing')
    if limit_error:
        return limit_error
    user = g.current_user
    data = request.get_json()
    image_b64 = data.get('image')
    if not image_b64:
        return jsonify({'error': 'No image provided.'}), 400
    if ',' in image_b64:
        image_b64 = image_b64.split(',')[1]
    image_bytes = base64.b64decode(image_b64)
    unknown_image = face_recognition.load_image_file(io.BytesIO(image_bytes))
    face_locations = face_recognition.face_locations(unknown_image)
    encodings = face_recognition.face_encodings(unknown_image, face_locations)
    if not encodings:
        return jsonify({'error': 'No faces found.'}), 404
    for encoding in encodings:
        db.session.add(TestingFaceEncoding(user_id=user.id, encoding=pickle.dumps(encoding)))
    db.session.commit()
    return jsonify({'message': 'Test face encoding(s) stored.'}), 201

@testing_bp.route('/check', methods=['POST'])
def check_testing():
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
    unknown_image = face_recognition.load_image_file(io.BytesIO(image_bytes))
    face_locations = face_recognition.face_locations(unknown_image)
    encodings = face_recognition.face_encodings(unknown_image, face_locations)
    if not encodings:
        return jsonify({'error': 'No faces found.'}), 404
    test_encodings = TestingFaceEncoding.query.filter_by(user_id=user.id).all()
    known_encodings = [pickle.loads(te.encoding) for te in test_encodings]
    found = False
    for unknown_encoding in encodings:
        matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=0.6)
        if True in matches:
            found = True
            break
    return jsonify({'exists': found}), 200
