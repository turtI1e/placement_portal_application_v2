from flask import Flask, jsonify, send_from_directory, current_app, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from extensions import cache
from config import Config
from flask_jwt_extended.exceptions import JWTDecodeError, NoAuthorizationError, InvalidHeaderError, WrongTokenError
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app(skip_jwt=False):
    app = Flask(__name__)
    app.config.from_object(Config)

    print("JWT_SECRET_KEY from config:", app.config.get('JWT_SECRET_KEY'))

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    cache.init_app(app)   # <-- initialize cache
    if not skip_jwt:
        jwt.init_app(app)
    CORS(app)

    app.db = db

    if not skip_jwt:
        @jwt.user_lookup_loader
        def user_lookup_callback(_jwt_header, jwt_data):
            identity = jwt_data["sub"]
            print(f"DEBUG: Looking up user with identity: {identity}")
            db = current_app.db
            from models import User
            user = db.session.get(User, int(identity))
            print(f"DEBUG: Found user: {user}")
            return user

        @jwt.unauthorized_loader
        def unauthorized_callback(error):
            return jsonify({"msg": "Missing or invalid authorization"}), 401

        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            print("🔥 INVALID TOKEN ERROR:", error)
            return jsonify({"msg": f"Invalid token: {error}"}), 422

        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_data):
            return jsonify({"msg": "Token has expired"}), 401

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    @app.route('/api/debug/auth', methods=['GET'])
    def debug_auth():
        auth = request.headers.get('Authorization')
        return jsonify({
            'auth_header': auth,
            'raw_token': auth.split('Bearer ')[-1] if auth and auth.startswith('Bearer ') else None,
            'token_length': len(auth.split('Bearer ')[-1]) if auth and auth.startswith('Bearer ') else 0
        })

    @app.route('/static/uploads/resumes/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
