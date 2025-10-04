from flask import Blueprint, request, jsonify, g
from Blueprint_app.middleware import verify_credentials
import base64
import face_recognition
import pickle
import io

face_bp = Blueprint('face', __name__, url_prefix='/api/v1/face')

@face_bp.route('/extract', methods=['POST'])
def extract_face():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
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
    encoding_list = [base64.b64encode(pickle.dumps(e)).decode('utf-8') for e in encodings]
    return jsonify({'encodings': encoding_list}), 200
