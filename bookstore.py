from pymongo import MongoClient
from bson.objectid import ObjectId

import datetime

def get_db():
    client = MongoClient('localhost:27017')
    db = client.bookstore
    return db

def add_books(db):
    db.books.insert(
        [{
            "_id": 1,
            "title": "Becoming",
            "author": ["Michelle Obama"],
            "language": "English",
            "isbn": "1524763136",
            "published_date": "2018-11-13",
            "publisher": "Crown Publishing Group"
        },{
            "_id": 2,
            "title": "Redemption",
            "author": ["David Baldacci"],
            "language": "English",
            "isbn": "1538761459",
            "published_date": "2019-10-08",
            "publisher": "Grand Central Publishing"
        },{
            "_id": 3,
            "title": "Milkman: A Novel",
            "author": ["Anna Burns"],
            "language": "English",
            "isbn": "1644450003",
            "published_date": "2018-12-04",
            "publisher": "Graywolf Press"
        }]
    )

def add_inventory(db):
    db.inventory.insert(
        [{
            "book_id": 1,
            "qty": 2,
            "last_modified": datetime.datetime.utcnow()
        },{
            "book_id": 2,
            "qty": 1,
            "last_modified": datetime.datetime.utcnow()
        },{
            "book_id": 3,
            "qty": 5,
            "last_modified": datetime.datetime.utcnow()
        }]
    )


def add_customer(db):
    db.customers.insert(
        [{
            "_id": 1,
            "name": "Karthik",
            "address": "San Jose, CA",
            "phone": "408-000-001",
            "last_modified": datetime.datetime.utcnow()
        },{
            "_id": 2,
            "name": "Muthu",
            "address": "San Jose, CA",
            "phone": "408-000-002",
            "last_modified": datetime.datetime.utcnow()
        },{
            "_id": 3,
            "name": "Anis",
            "address": "San Jose, CA",
            "phone": "408-000-003",
            "last_modified": datetime.datetime.utcnow()
        }]
    )


def get_book(db, book_id):
    return db.books.find_one({'_id': book_id})


def get_inventory(db):
    return db.inventory.find({})


def get_customer(db, customer_id):
    return db.customers.find_one({'_id': customer_id})

def get_orders(db):
    return db.orders.find({})


def get_available_books(db):
    available_books = []
    for record in db.inventory.find({}):
        book_id = record['book_id']
        qty = record['qty']
        if qty <= 0:
            continue
        book = db.books.find_one({'_id': book_id})
        book['qty'] = qty
        available_books.append(book)
    return available_books


def place_order(db, customer_id, book_id, qty):
    db.orders.insert({
            "customer_id": customer_id,
            "book_id": book_id,
            "qty": qty,
            "status": "Created"
        })

    print("Order placed successfully.")

def fullfil_order(db, order_id):
    current_order = db.orders.find_one({"_id": order_id})
    current_inventory = db.inventory.find_one({"book_id": current_order['book_id']})
    balance = current_inventory['qty'] - current_order['qty']
    if balance >= 0:
        db.orders.update_one({"_id": current_order['_id']}, {"$set": {"status": "fullfilled"}})
        db.inventory.update_one({"_id": current_inventory['_id']}, {"$set": {"qty": balance}})
        print("Order fullfilled successfully.")
    else:
        raise ValueError("Can't fullfil this order. Not enough books in inventory.")

if __name__ == "__main__":
    db = get_db()
    db["books"].delete_many({})
    db["inventory"].delete_many({})
    db["customers"].delete_many({})
    db["orders"].delete_many({})
    add_books(db)
    add_customer(db)
    add_inventory(db)
    
    print("\n Current Inventory:")
    print("Book Title", "Quantity")
    for book in get_available_books(db):
        print(book['title'], book['qty'])

    print("\n Place some orders ...")
    place_order(db, 1, 1, 2)
    place_order(db, 2, 2, 2)

    print("\n Current Orders:")
    print("Order ID", "Customer ID", "Book ID", "Quantity", "Status")
    for order in get_orders(db): 
        print(order['_id'], order['customer_id'], order['book_id'], order['qty'], order['status'])

    print("\n Fullfilling the order for customer 1 ...")
    order = db.orders.find_one({"customer_id": 1})
    fullfil_order(db, order['_id'])

    print("\n Updated Inventory:")
    print("Book Title", "Quantity")
    for book in get_available_books(db):
        print(book['title'], book['qty'])

    print("\n Updated Orders:")
    print("Order ID", "Customer ID", "Book ID", "Quantity", "Status")
    for order in get_orders(db): 
        print(order['_id'], order['customer_id'], order['book_id'], order['qty'], order['status'])


    print("\n Fullfilling the order for customer 2 ...")
    order = db.orders.find_one({"customer_id": 2})
    fullfil_order(db, order['_id'])