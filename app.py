from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from config import Config
from api.routes import api

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# Register API blueprint
app.register_blueprint(api)


@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


@app.route('/manifest.json')
def manifest():
    """Serve the PWA manifest file"""
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')


@app.route('/service-worker.js')
def service_worker():
    """Serve the service worker file"""
    return send_from_directory('.', 'service-worker.js', mimetype='application/javascript')


@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok'}, 200


if __name__ == '__main__':
    port = int(app.config.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
