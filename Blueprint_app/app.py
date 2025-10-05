import os
import logging

from requests import request
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from Blueprint_app.tasks import cleanup_testing_encodings

# Load environment variables from the .env file for local development
load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
         
        
    app = Flask(__name__, template_folder="templates")
    
    # Use environment variables for the database connection URI
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.secret_key = os.getenv("SECRET_KEY", "Some Key")
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # db initialization
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Initializing Login Manager
    login_manager.init_app(app)
    
    from Blueprint_app.models import Student
    @login_manager.user_loader
    def load_user(user_id):
        # The user_id passed here is the student's ID
        return Student.query.get(user_id)
    
    # Configure the unauthorized handler
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return "Unauthorized", 403
    
    from Blueprint_app.middleware import global_rate_limit
    @app.before_request
    def before_request_func():
        limit_error = global_rate_limit()
        if limit_error:
            return limit_error
    
    @app.route("/", methods=["GET"])
    def welcome():
        return {"message": "Welcome to the Facial Recognition API!"}
    
    # Setup logging to file for endpoint access
    logging.basicConfig(
        filename='access.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    @app.before_request
    def log_request():
        user = getattr(getattr(g, 'current_user', None), 'email', None)
        logging.info(f"{request.method} {request.path} | User: {user}")
    
    # Enable CORS for the entire application
    CORS(app)
    
    # import and register blueprints
    from Blueprint_app.blueprints.auth import auth_bp
    from Blueprint_app.blueprints.face import face_bp
    from Blueprint_app.blueprints.attendance import attendance_bp
    from Blueprint_app.blueprints.testing import testing_bp
    from Blueprint_app.blueprints.analytics import analytics_bp
    from Blueprint_app.blueprints.person import person_bp
    from Blueprint_app.blueprints.person_analytics import person_analytics_bp
    from Blueprint_app.blueprints.webhook import webhook_bp
    from Blueprint_app.blueprints.auditlog import auditlog_bp
    from Blueprint_app.blueprints.admin import admin_bp
    from Blueprint_app.blueprints.mfa import mfa_bp
    from Blueprint_app.blueprints.openapi import openapi_bp
    from Blueprint_app.blueprints.bulk import bulk_bp
    from Blueprint_app.blueprints.health import health_bp
    from Blueprint_app.blueprints.payment import payment_bp
    from Blueprint_app.blueprints.paystack import paystack_bp
    from Blueprint_app.blueprints.intlpay import intlpay_bp
    app.register_blueprint(person_analytics_bp)
    app.register_blueprint(person_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(face_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(testing_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(auditlog_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(mfa_bp)
    app.register_blueprint(openapi_bp)
    app.register_blueprint(bulk_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(paystack_bp)
    app.register_blueprint(intlpay_bp)
    
    # db migrations
    migrate = Migrate(app, db)

    # Start APScheduler for periodic cleanup
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_testing_encodings, 'interval', hours=24)
    scheduler.start()
    app.scheduler = scheduler

    return app