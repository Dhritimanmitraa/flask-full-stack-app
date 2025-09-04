import sys
import os

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask

# Create a minimal Flask app for testing
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Vercel! Flask is working!"

@app.route('/health')
def health():
    return {"status": "ok", "message": "Flask app is running on Vercel"}

if __name__ == '__main__':
    app.run(debug=True)
