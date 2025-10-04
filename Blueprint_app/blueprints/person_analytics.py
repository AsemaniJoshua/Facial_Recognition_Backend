from flask import Blueprint, jsonify, g, request, Response
from Blueprint_app.models import Person, PersonAttendance
from Blueprint_app.middleware import verify_credentials
import csv
import io
from sqlalchemy import func

person_analytics_bp = Blueprint('person_analytics', __name__, url_prefix='/api/v1/person/analytics')

# List persons with filters
@person_analytics_bp.route('/list', methods=['GET'])
def list_persons():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    query = Person.query.filter_by(user_id=user.id)
    # Filters
    age = request.args.get('age')
    name = request.args.get('name')
    min_attendance = request.args.get('min_attendance')
    if age:
        query = query.filter(Person.age == int(age))
    if name:
        query = query.filter(func.lower(Person.first_name + ' ' + (Person.middle_name or '') + ' ' + Person.last_name).like(f'%{name.lower()}%'))
    persons = query.all()
    result = []
    for p in persons:
        attendance_count = PersonAttendance.query.filter_by(person_id=p.id, user_id=user.id).count()
        if min_attendance and attendance_count < int(min_attendance):
            continue
        result.append({
            'id': p.id,
            'first_name': p.first_name,
            'middle_name': p.middle_name,
            'last_name': p.last_name,
            'age': p.age,
            'created_at': p.created_at,
            'attendance_count': attendance_count
        })
    return jsonify({'persons': result}), 200

# Export persons as CSV
@person_analytics_bp.route('/export/csv', methods=['GET'])
def export_persons_csv():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    persons = Person.query.filter_by(user_id=user.id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'first_name', 'middle_name', 'last_name', 'age', 'created_at'])
    for p in persons:
        writer.writerow([p.id, p.first_name, p.middle_name, p.last_name, p.age, p.created_at])
    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=persons.csv"})

# Export attendance records for a person as CSV
@person_analytics_bp.route('/attendance/export/csv/<int:person_id>', methods=['GET'])
def export_attendance_csv(person_id):
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    records = PersonAttendance.query.filter_by(person_id=person_id, user_id=user.id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['attendance_id', 'person_id', 'timestamp'])
    for r in records:
        writer.writerow([r.id, r.person_id, r.timestamp])
    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": f"attachment;filename=attendance_{person_id}.csv"})

# Export persons as JSON
@person_analytics_bp.route('/export/json', methods=['GET'])
def export_persons_json():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    persons = Person.query.filter_by(user_id=user.id).all()
    result = []
    for p in persons:
        result.append({
            'id': p.id,
            'first_name': p.first_name,
            'middle_name': p.middle_name,
            'last_name': p.last_name,
            'age': p.age,
            'created_at': p.created_at
        })
    return jsonify({'persons': result}), 200

# Export attendance records for a person as JSON
@person_analytics_bp.route('/attendance/export/json/<int:person_id>', methods=['GET'])
def export_attendance_json(person_id):
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    records = PersonAttendance.query.filter_by(person_id=person_id, user_id=user.id).all()
    result = []
    for r in records:
        result.append({
            'attendance_id': r.id,
            'person_id': r.person_id,
            'timestamp': r.timestamp
        })
    return jsonify({'attendance_records': result}), 200

# Summary stats
@person_analytics_bp.route('/summary', methods=['GET'])
def summary_stats():
    cred_error = verify_credentials()
    if cred_error:
        return cred_error
    user = g.current_user
    total_persons = Person.query.filter_by(user_id=user.id).count()
    total_attendance = PersonAttendance.query.filter_by(user_id=user.id).count()
    most_frequent = None
    freq = 0
    for p in Person.query.filter_by(user_id=user.id).all():
        count = PersonAttendance.query.filter_by(person_id=p.id, user_id=user.id).count()
        if count > freq:
            freq = count
            most_frequent = p.id
    return jsonify({
        'total_persons': total_persons,
        'total_attendance': total_attendance,
        'most_frequent_person_id': most_frequent,
        'most_frequent_attendance_count': freq
    }), 200
