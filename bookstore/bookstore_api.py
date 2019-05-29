from flask import request, jsonify, Blueprint, _request_ctx_stack, make_response
from bson.objectid import ObjectId
from bookstore import bookstore_data
from bookstore.bookstore_db import get_db
from bookstore.crossdomain import crossdomain
import datetime
import json
import ast
import imp
from jose import jwt
from functools import wraps
import requests
###Added for Auth######

from six.moves.urllib.request import urlopen
from flask_cors import cross_origin
### aded _request_ctx_stack in beg
 
###################################
bp = Blueprint('bookstore_api', __name__, url_prefix='/api/v1/')

#####
AUTH0_DOMAIN = 'dev-93vs-avb.auth0.com'
#API_AUDIENCE = 'https://dev-93vs-avb.auth0.com/api/v2/'
API_AUDIENCE = 'https://bookstore/api'
ALGORITHMS = ["RS256"]
####


#app.config['SECRET_KEY'] = 'aquickfoxjumpedovertheriver~!@`123`'

# Format error response and append status code.
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

###############################

def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


##########################################################################` 
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
    print "inside Get the header details"
    auth = request.headers.get("Authorization", None)
    print request.headers
    print auth
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

def userauthn(auth):
    headers = {
     'content-type': 'application/x-www-form-urlencoded',
    }

    data = {
      'grant_type': 'password',
      'audience': 'https://bookstore/api',
      'scope': 'read:sample',
      'client_id': 'D89f7KGFSngsOTjzsvPEVeJXFlhMgMGd',
      'client_secret': 'yiDQVTdD30ZNVvp_K7-1UHRvsOa3JBEevflvd5l443ytGZhp2_lqB-N5IUKgcD9-'
    }
    data ["username"] = auth.username
    data ["password"] = auth.password
    print data
     
    print type(data)
    response = requests.post('https://dev-93vs-avb.auth0.com/oauth/token', headers=headers, data=data)
    print response
    return jsonify (response.text) 
    print "exiting function 1"

@bp.route('/loginui', methods=['GET','OPTIONS'])
@crossdomain(origin='*')
def loginui(*args, **kwargs):
	if request.authorization:
		print "auth header present"
	else:
		print "no auth present"   
    	try:
        	access_token=userauthn(request.authorization)
    	except Exception as ex:
        	make_response(jsonify(ex), 401)
        	print(ex)
        	print "debug1"
        	return json_error_response("Authentication Failure.", 401) 
    	return (access_token)


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
#@token_required
@requires_auth
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
@requires_auth
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


@bp.route("orders", methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
@requires_auth
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
#@token_required
#@requires_auth
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


# This does need authentication
@bp.route("private")
#@cross_origin(headers=['Content-Type', 'Authorization'])
@crossdomain(origin='*')
@requires_auth
def private():
    response = "Hello from a private endpoint! You need to be authenticated to see this."
    return jsonify(message=response)
