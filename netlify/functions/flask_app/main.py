import os
import sys
from flask import Flask

# Add the project directory to the path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from run import app # Assuming your Flask app instance is named 'app' in run.py

def handler(event, context):
    from netlify_integration import run_wsgi_app # This will be created next
    return run_wsgi_app(app, event, context)
