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

from app import create_app

# Create the Flask application
app = create_app()

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
