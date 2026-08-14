"""NutriTrack — Flask Application with Security Middleware"""

from flask import Flask, jsonify, request
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Security Headers Middleware
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        return response

    # Global Error Handlers (Prevents stack trace / internal server leaks)
    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad Request', 'message': 'Invalid input data.'}), 400
        return 'Bad Request', 400

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not Found', 'message': 'The requested resource was not found.'}), 404
        return 'Not Found', 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Method Not Allowed', 'message': 'HTTP method not supported for this endpoint.'}), 405
        return 'Method Not Allowed', 405

    @app.errorhandler(500)
    def internal_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred.'}), 500
        return 'Internal Server Error', 500

    # Register blueprints
    from routes.pages import pages
    from routes.api import api

    app.register_blueprint(pages)
    app.register_blueprint(api)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, port=5000)
