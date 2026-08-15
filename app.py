import os
import secrets
from flask import Flask, jsonify, request, session, render_template
from config import Config
from database import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from routes import routes
    app.register_blueprint(routes)

    @app.before_request
    def validate_host():
        trusted = app.config.get('TRUSTED_HOSTS')
        if trusted and not app.config.get('TESTING'):
            req_host = request.host.split(':')[0].lower()
            allowed = [h.lower() for h in trusted]
            is_prod = app.config.get('SESSION_COOKIE_SECURE', False)
            if req_host not in allowed and (is_prod or req_host not in ['localhost', '127.0.0.1']):
                return jsonify({'error': 'Bad Request', 'message': 'Untrusted host header.'}), 400

    @app.before_request
    def manage_csrf():
        # Ensure session contains a cryptographic CSRF token
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)

        # Skip CSRF check in testing mode or for safe read-only methods
        if app.config.get('TESTING') or request.method in ['GET', 'HEAD', 'OPTIONS']:
            return None

        # Verify CSRF token from request header or form data
        header_token = request.headers.get('X-CSRFToken') or request.headers.get('X-CSRF-Token')
        form_token = request.form.get('csrf_token')
        expected_token = session.get('csrf_token')

        if not expected_token or (header_token != expected_token and form_token != expected_token):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Forbidden', 'message': 'CSRF token missing or invalid.'}), 403
            return render_template('base.html', custom_error='403 Forbidden: Invalid or missing CSRF token.'), 403

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        # Add HSTS in production/HTTPS environments
        if app.config.get('SESSION_COOKIE_SECURE') or request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Content Security Policy: whitelist self, fonts from Google, and local static assets
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers['Content-Security-Policy'] = '; '.join(csp_directives)
        return response

    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad Request', 'message': 'Invalid request parameters.'}), 400
        return 'Bad Request', 400

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden', 'message': 'Access forbidden.'}), 403
        return 'Forbidden', 403

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
    # Read debug setting from environment; default False in standalone execution
    is_debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=is_debug, port=port)
