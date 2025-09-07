import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager

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
    
    # Enable CORS for the entire application
    CORS(app)
    
    # import and register blueprints
    from Blueprint_app.blueprints.attendance.routes import attendance
    from Blueprint_app.blueprints.core.routes import core
    from Blueprint_app.blueprints.dashboard.routes import dashboard_bp
    from Blueprint_app.blueprints.students.routes import students
    
    
    app.register_blueprint(attendance, url_prefix="/api/v1")
    app.register_blueprint(core, url_prefix="/")
    app.register_blueprint(dashboard_bp, url_prefix="/api/v1")
    app.register_blueprint(students, url_prefix='/api/v1')
    
    # db migrations
    migrate = Migrate(app, db)
    return app