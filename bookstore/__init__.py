from os import environ as env
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from functools import wraps

from bookstore.version import API_VERSION

import jwt
import datetime

JWT_SECRET_KEY = env.get('JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    JWT_SECRET_KEY = "aquickfoxjumpedovertheriver"


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def fulfillment_token(auth):
    if auth and auth.password == 'secret':
        user_name = auth.username
    else:
        return jsonify_error("Unauthorized", 401)
        
    try:
        token = jwt.encode({'user': user_name, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)}, JWT_SECRET_KEY)
        return jsonify({'token': token.decode()})
    except Exception as ex:
        print(ex)
        return jsonify_error("Unexpected error while creating the auth token.", 500)

def jsonify_error(message, staus_code):
    error = {
        'apiVersion': API_VERSION,
        'status_code': staus_code,
        'message': message
    }
    return (jsonify(error), staus_code)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = get_token_auth_header()

            jwt.decode(token, JWT_SECRET_KEY)
        except AuthError as ex:
            return jsonify_error(ex.error, ex.status_code)
        except Exception as ex:
            print(ex)
            return jsonify_error("Unauthorized", 403)

        return f(*args, **kwargs)

    return decorated


def get_token_auth_header():
    """Obtains the access token from the Authorization Header"""

    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError("Authorization header not found", 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError("Authorization header must start with Bearer", 401)
    elif len(parts) == 1:
        raise AuthError("Token not found", 401)
    elif len(parts) > 2:
        raise AuthError("Authorization header must be Bearer token", 401)

    token = parts[1]
    return token


def create_app(app_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    FLASK_SECRET_KEY = env.get('FLASK_SECRET_KEY')
    if not FLASK_SECRET_KEY:
        FLASK_SECRET_KEY = "secretdev"

    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY=FLASK_SECRET_KEY,
    )

    if app_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(app_config)

    @app.route("/")
    def index():
        message = {
            'apiVersion': API_VERSION,
            'status_code': 200,
            'message': 'Welcome to the BookStore API'
        }
        return jsonify(message)

    @app.route('/status')
    def status():
        message = {
            'apiVersion': API_VERSION,
            'status_code': 200,
            'message': 'OK'
        }
        return jsonify(message)

    @app.errorhandler(404)
    def page_not_found(e):
        """Send message to the user with notFound 404 status."""
        return jsonify_error("Page Not Found. Refer to the API documentation.", 404)

    @app.errorhandler(Exception)
    def error_handler(ex):
        print(ex)
        status_code = (ex.code if isinstance(ex, HTTPException) else 500)
        message = {
            'apiVersion': API_VERSION,
            'status_code': status_code,
            'message': str(ex)
        }
        response = jsonify(message)
        response.status_code = status_code
        return response


    # register the database commands
    from bookstore import bookstore_db
    bookstore_db.init_app(app)

    # apply the blueprints to the app
    from bookstore import bookstore_api
    app.register_blueprint(bookstore_api.bp)

    return app
