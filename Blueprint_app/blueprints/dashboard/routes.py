from flask import Blueprint, jsonify
from ...models import DashboardMetrics, Chart, AttendanceMetrics

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    metrics = DashboardMetrics.query.all()
    return jsonify([{'title': m.title, 'value': m.value, 'description': m.description} for m in metrics])

@dashboard_bp.route('/dashboard/chart', methods=['GET'])
def get_chart_data():
    chart_data = Chart.query.all()
    return jsonify([{'day': c.day, 'present': c.present, 'absent': c.absent} for c in chart_data])

@dashboard_bp.route('/attendance/metrics', methods=['GET'])
def get_attendance_metrics():
    metrics = AttendanceMetrics.query.all()
    return jsonify([{'title': m.title, 'value': m.value} for m in metrics])
