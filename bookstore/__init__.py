import os
from flask import Flask, jsonify


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    @app.route("/")
    def index():
        message = {
            'apiVersion': 'v1.0.0',
            'status': 200,
            'message': 'Welcome to the BookStore API'
        }
        return jsonify(message)

    @app.route('/status')
    def status():
        message = {
            'apiVersion': 'v1.0.0',
            'status': 200,
            'message': 'OK'
        }
        return jsonify(message)

    # register the database commands
    from bookstore import bookstore_db
    bookstore_db.init_app(app)

    # apply the blueprints to the app
    from bookstore import bookstore_api
    app.register_blueprint(bookstore_api.bp)

    return app
