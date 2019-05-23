from flask import request, jsonify, Blueprint
from bson.objectid import ObjectId
from bookstore import bookstore_data
from bookstore.bookstore_db import get_db
from bookstore.crossdomain import crossdomain
import datetime
import json
import ast
import imp
import jwt
from functools import wraps

bp = Blueprint('bookstore_api', __name__, url_prefix='/api/v1/')

#app.config['SECRET_KEY'] = 'aquickfoxjumpedovertheriver~!@`123`'

# Format error response and append status code.
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

 
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        try:
            jwt.decode(token, 'aquickfoxjumpedovertheriver')
        except:
            return json_error_response("Token is invalid", 403)

        return f(*args, **kwargs)

    return decorated

 
def get_token_auth_header():
    """Obtains the access token from the Authorization Header"""
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing", "description": "Authorization header is expected"}, 401)

    parts = auth.split()
    print(parts)

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description": "Authorization header must start with Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    print(token)
    return token

def json_error_response(message, staus_code):
    error = {
        'status': staus_code,
        'message': message
    }
    return (jsonify(error), staus_code)


def basic_authenticate_user_credentials(auth):
    if auth and auth.password == 'secret':
        return auth.username
    else:
        raise AuthError({"code": "401", "description": "Authorization header is expected"}, 401)

@bp.route('/login')
def login():
    try:
        user_name = basic_authenticate_user_credentials(request.authorization)
    except Exception as ex:
        print(ex)
        return json_error_response("Authentication Failure.", 401)

    token = jwt.encode({'user' : user_name, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=120)}, 'aquickfoxjumpedovertheriver')
    return jsonify({'token' : token.decode()})
    

@bp.route("books", methods=['GET'])
@crossdomain(origin='*')
def get_all_books():
    """
       API to get all the books in the bookstore.
       """
    try:
        books = bookstore_data.get_all_books(get_db())
        return jsonify(books)
    except Exception as ex:
        print(ex)
        return json_error_response("Error while retrieving the list of books", 500)


@bp.route("books/<isbn>", methods=['GET'])
@crossdomain(origin='*')
@token_required
def get_book(isbn):
    """
       API to get the details of a book.
       """
    try:
        book = bookstore_data.get_book_by_isbn(get_db(), isbn)
        if book is None:
            return json_error_response("No books found for the given isbn", 404)
        else:
            return jsonify(book)

    except Exception as ex:
        print(ex)
        return json_error_response("Error while searching the book by isbn", 500)


@bp.route("orders", methods=['GET'])
@crossdomain(origin='*')
@token_required
def get_all_orders():
    """
       API to get all the orders.
       """
    try:
        orders = bookstore_data.get_orders(get_db())
        return jsonify(orders)
    except Exception as ex:
        print(ex)
        return json_error_response("Error while retrieving the list of orders", 500)


@bp.route("orders", methods=['POST'])
@crossdomain(origin='*')
@token_required
def place_order():
    """
       API to create new order.
       """
    try:
        # Create new order
        try:
            order_data = request.get_json(force="true")
            customer_id = order_data['customer_id']
            items = order_data['items']
        except Exception as ex:
            print(ex)
            return json_error_response("Invalid input in order details", 404)

        order = bookstore_data.place_order(get_db(), customer_id, items)
        return jsonify(order)
    except Exception as ex:
        print(ex)
        return json_error_response("Error while placing the order", 500)


@bp.route("orders/<order_id>", methods=['GET'])
@crossdomain(origin='*')
@token_required
def get_order(order_id):
    """
       API to get the order details.
       """
    try:
        _id = ObjectId(order_id)
        order = bookstore_data.get_order_by_id(get_db(), _id)
        return jsonify(order)
    except Exception as ex:
        print(ex)
        return json_error_response("Unexpected error while retrieving the order.", 500)


@bp.route("orders/<order_id>", methods=['PUT'])
@crossdomain(origin='*')
@token_required
def fulfill_order(order_id):
    """
       API to fulfill an existing order.
       """
    try:
        _id = ObjectId(order_id)
        order = bookstore_data.fulfill_order(get_db(), _id)
        return jsonify(order)
    except ValueError as ve:
        return json_error_response(str(ve), 404)
    except Exception as ex:
        return json_error_response("Unexpected error while fulfilling the order. " + str(ex), 500)


@bp.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    return json_error_response("Page Not Found. Refer to the API documentation.", 404)
