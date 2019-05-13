from bson.objectid import ObjectId
import datetime


def get_all_books(db):
    books = []
    for book in db.books.find({}):
        book['qty'] = get_inventory_quantity_by_book_id(db, book['_id'])
        book['_id'] = str(book['_id'])
        books.append(book)
    return books


def get_available_books(db):
    available_books = []
    for record in db.inventory.find({'qty': {"$gt": 0}}):
        book = get_book_by_id(db, record['book_id'])
        book['qty'] = record['qty']
        book['_id'] = str(book['_id'])
        available_books.append(book)
    return available_books


def get_book_by_isbn(db, isbn):
    book = db.books.find_one({'isbn': isbn})
    if book != None:
        book['qty'] = get_inventory_quantity_by_book_id(db, book['_id'])
        book['_id'] = str(book['_id'])
    return book


def get_book_by_id(db, book_id):
    book = db.books.find_one({'_id': book_id})
    if book != None:
        book['qty'] = get_inventory_quantity_by_book_id(db, book['_id'])
        book['_id'] = str(book['_id'])
    return book


def get_inventory_quantity_by_book_id(db, book_id):
    record = db.inventory.find_one({'book_id': book_id})
    if record != None:
        return record['qty']
    else:
        return None


def get_customers(db):
    customers = []
    for customer in db.customers.find({}):
        customer['_id'] = str(customer['_id'])
        customers.append(customer)
    return customers


def get_customer_by_id(db, customer_id):
    customer = db.customers.find_one({'_id': customer_id})
    if customer != None:
        customer['_id'] = str(customer['_id'])
    return customer


def get_orders(db):
    orders = []
    for order in db.orders.find({}):
        order['_id'] = str(order['_id'])
        orders.append(order)
    return orders


def get_order_by_id(db, order_id):
    order = db.orders.find_one({'_id': ObjectId(order_id)})
    if order != None:
        order['_id'] = str(order['_id'])
    return order


def place_order(db, customer_id, items):
    order = {
        "customer_id": customer_id,
        "items": items,
        "status": "Created"
    }

    result = db.orders.insert_one(order)
    order = db.orders.find_one({'_id': result.inserted_id})
    if order != None:
        order['_id'] = str(order['_id'])
    return order


def fulfill_order(db, order_id):
    current_order = db.orders.find_one({'_id': ObjectId(order_id)})

    if current_order['status'] == 'Fulfilled':
        raise ValueError("This order is already fulfilled.")

    is_fulfillable = True
    print "test2"
    print ("order-ID:"+str(order_id))
    for item in current_order['items']:
        current_inventory = db.inventory.find_one({"book_id": item['book_id']})
        balance = current_inventory['qty'] - int(item['qty'])
        if balance < 0:
             is_fulfillable = False
             break

    if is_fulfillable:
        for item in current_order['items']:
            balance = current_inventory['qty'] - int(item['qty'])
            db.orders.update_one({"_id": current_order['_id']}, {"$set": {"status": "Fulfilled"}})
            db.inventory.update_one({"_id": current_inventory['_id']}, {"$set": {"qty": balance}})
        return get_order_by_id(db, order_id)
    else:
        raise ValueError("Can't fulfill this order. Not enough books in inventory.")


if __name__ == "__main__":

    from bookstore import create_app
    from bookstore import bookstore_db

    app = create_app({
        'TESTING': True,
    })

    with app.app_context():
        db = bookstore_db.init_db()

        print("\n Current Inventory:")
        print("Book Title", "Quantity")
        for book in get_available_books(db):
            print(book['title'], book['qty'])

        print("\n Place some orders ...")
        place_order(db, 1, [{"book_id": "0123456789ab012345678901", "qty": 2}, {"book_id": "0123456789ab012345678901", "qty": 1}])
        place_order(db, 2, [{"book_id": "0123456789ab012345678902", "qty": 2}, {"book_id": "0123456789ab012345678901", "qty": 1}])

        print("\n Current Orders:")
        print("Order ID", "Customer ID", "Book ID", "Quantity", "Status")
        for order in get_orders(db):
            print(order['_id'], order['customer_id'], order['items'], order['status'])

        print("\n fulfillling the order for customer 1 ...")
        order = db.orders.find_one({"customer_id": 1})
        fulfill_order(db, order['_id'])

        print("\n Updated Inventory:")
        print("Book Title", "Quantity")
        for book in get_available_books(db):
            print(book['title'], book['qty'])

        print("\n Updated Orders:")
        print("Order ID", "Customer ID", "Book ID", "Quantity", "Status")
        for order in get_orders(db):
            print(order['_id'], order['customer_id'], order['items'], order['status'])

        print("\n fulfillling the order for customer 2 ...")
        order = db.orders.find_one({"customer_id": 2})
        fulfill_order(db, order['_id'])
