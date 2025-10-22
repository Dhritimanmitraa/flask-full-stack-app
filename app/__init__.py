from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()

def create_app():
    """Application factory"""
    instance_path = os.environ.get('FLASK_INSTANCE_PATH')
    
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static',
                instance_path=instance_path,
                instance_relative_config=False)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads')
    app.config['UPLOAD_FOLDER_IMAGES'] = os.path.join(app.config['UPLOAD_FOLDER'], 'images')
    app.config['UPLOAD_FOLDER_VIDEOS'] = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Create upload directories if they don't exist (skip in serverless environments)
    try:
        upload_folders = [
            app.config['UPLOAD_FOLDER'],
            app.config['UPLOAD_FOLDER_IMAGES'],
            app.config['UPLOAD_FOLDER_VIDEOS']
        ]
        for folder in upload_folders:
            # Only create directories if not in a read-only serverless environment
            if not '/var/task' in str(folder) and not '/tmp' in str(folder):
                os.makedirs(folder, exist_ok=True)
    except Exception as e:
        print(f"Note: Could not create upload directories (serverless mode): {e}")
    
    db.init_app(app)
        
    login_manager.init_app(app)
    csrf.init_app(app)
    moment.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    from app.routes import main_bp, auth_bp, api_bp, admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    pass
    
    return app 