from flask import Blueprint, jsonify

core = Blueprint('core', __name__)

@core.route('/')
def index():
    return jsonify({"success": True, "message": "Welcome to the Facial Recognition Backend"})
