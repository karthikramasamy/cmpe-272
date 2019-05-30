from flask import request, jsonify, Blueprint, _request_ctx_stack, make_response
from os import environ as env
from bson.objectid import ObjectId
from bookstore import token_required
from bookstore import bookstore_data
from bookstore import jsonify_error
from bookstore.bookstore_db import get_db
from bookstore.crossdomain import crossdomain

bp = Blueprint('bookstore_api', __name__, url_prefix='/api/v1/')

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
        return jsonify_error("Error while retrieving the list of books", 500)


@bp.route("books/<isbn>", methods=['GET'])
@crossdomain(origin='*')
def get_book(isbn):
    """
       API to get the details of a book.
       """
    try:
        book = bookstore_data.get_book_by_isbn(get_db(), isbn)
        if book is None:
            return jsonify_error("No books found for the given isbn", 404)
        else:
            return jsonify(book)

    except Exception as ex:
        print(ex)
        return jsonify_error("Error while searching the book by isbn", 500)


@bp.route("orders", methods=['GET'])
@crossdomain(origin='*')
def get_all_orders():
    """
       API to get all the orders.
       """
    try:
        orders = bookstore_data.get_orders(get_db())
        return jsonify(orders)
    except Exception as ex:
        print(ex)
        return jsonify_error("Error while retrieving the list of orders", 500)


@bp.route("orders", methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
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
            return jsonify_error("Invalid input in order details", 404)

        order = bookstore_data.place_order(get_db(), customer_id, items)
        return jsonify(order)
    except Exception as ex:
        print(ex)
        return jsonify_error("Error while placing the order", 500)


@bp.route("orders/<order_id>", methods=['GET'])
@crossdomain(origin='*')
def get_order(order_id):
    """
       API to get the order details.
       """
    try:
        _id = ObjectId(order_id)
        order = bookstore_data.get_order_by_id(get_db(), _id)
        
        if order == None:
            return jsonify_error("Can't find any orders for the given id.", 404)
        else:
            return jsonify(order)
    except Exception as ex:
        print(ex)
        return jsonify_error("Unexpected error while retrieving the order.", 500)


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
        return jsonify_error(str(ve), 404)
    except Exception as ex:
        return jsonify_error("Unexpected error while fulfilling the order. " + str(ex), 500)

