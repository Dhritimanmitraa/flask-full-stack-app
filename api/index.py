import sys
import os

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# For serverless environment, set writable instance path
if os.environ.get('DATABASE_URL'):
    os.environ['FLASK_INSTANCE_PATH'] = '/tmp'
    
    # Monkey patch os.makedirs to handle read-only filesystem
    original_makedirs = os.makedirs
    def safe_makedirs(path, *args, **kwargs):
        # Skip directory creation in serverless read-only areas
        if '/var/task' in str(path) or 'instance' in str(path):
            return
        return original_makedirs(path, *args, **kwargs)
    os.makedirs = safe_makedirs

from app import create_app, db
from sqlalchemy import text, inspect

# Create the Flask application
app = create_app()

# Run database migration on serverless startup
with app.app_context():
    try:
        # Check if using PostgreSQL
        inspector = inspect(db.engine)
        if db.engine.dialect.name == 'postgresql':
            # Get table columns
            columns = [col['name'] for col in inspector.get_columns('post')]
            
            # Add image_filename column if it doesn't exist
            if 'image_filename' not in columns:
                try:
                    db.session.execute(text("ALTER TABLE post ADD COLUMN image_filename VARCHAR(255)"))
                    db.session.commit()
                    print("[MIGRATION] Added image_filename column")
                except Exception as e:
                    print(f"[MIGRATION] Error adding image_filename: {e}")
                    db.session.rollback()
            
            # Add video_filename column if it doesn't exist
            if 'video_filename' not in columns:
                try:
                    db.session.execute(text("ALTER TABLE post ADD COLUMN video_filename VARCHAR(255)"))
                    db.session.commit()
                    print("[MIGRATION] Added video_filename column")
                except Exception as e:
                    print(f"[MIGRATION] Error adding video_filename: {e}")
                    db.session.rollback()
    except Exception as e:
        print(f"[MIGRATION] Migration error: {e}")

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
