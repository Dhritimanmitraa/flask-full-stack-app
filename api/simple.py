import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify

# Create Flask app with custom instance path for Vercel
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static',
            instance_path='/tmp')

# Basic configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'

@app.route('/')
def index():
    """Simple home page"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flask Blog - Deployed on Vercel</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="text-center py-5 mb-5 bg-light rounded-3">
                <h1 class="display-4 fw-bold mb-4">🎉 Flask Blog is Live!</h1>
                <p class="lead text-muted">Successfully deployed from Render to Vercel</p>
                <div class="mt-4">
                    <span class="badge bg-success fs-6 me-2">✅ Vercel Deployment</span>
                    <span class="badge bg-info fs-6 me-2">✅ Flask Running</span>
                    <span class="badge bg-warning fs-6">🔄 Database Setup Pending</span>
                </div>
            </div>
            
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="card shadow-sm">
                        <div class="card-body p-4">
                            <h4 class="card-title mb-3">🚀 Migration Successful!</h4>
                            <p class="card-text">
                                Your Flask application has been successfully migrated from Render to Vercel! 
                                The basic Flask functionality is working perfectly.
                            </p>
                            <p class="card-text">
                                <strong>Next steps:</strong>
                            </p>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item">✅ Vercel deployment configured</li>
                                <li class="list-group-item">✅ Environment variables set</li>
                                <li class="list-group-item">✅ Database connection configured</li>
                                <li class="list-group-item">🔄 Create database tables</li>
                                <li class="list-group-item">🔄 Enable full app functionality</li>
                            </ul>
                            
                            <div class="mt-4">
                                <a href="/health" class="btn btn-primary">Health Check</a>
                                <a href="/test" class="btn btn-outline-primary">Test Endpoint</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="mt-5 py-4 bg-dark text-light text-center">
            <p>&copy; 2024 Flask Blog - Powered by Vercel</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Flask blog is running on Vercel!',
        'environment': 'production' if os.environ.get('DATABASE_URL') else 'development'
    })

@app.route('/test')
def test():
    """Test endpoint"""
    return "Flask Blog App is working on Vercel! 🚀"

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': '404 - Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '500 - Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
