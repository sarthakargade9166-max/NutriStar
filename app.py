import os
from flask import Flask, jsonify, request
from config import Config
from database import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from routes import routes
    app.register_blueprint(routes)

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad Request', 'message': 'Invalid request parameters.'}), 400
        return 'Bad Request', 400

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not Found', 'message': 'The requested resource was not found.'}), 404
        return 'Not Found', 404

    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred.'}), 500
        return 'Internal Server Error', 500

    with app.app_context():
        db.create_all()
        from seed_data import seed_foods_if_empty
        seed_foods_if_empty()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
