import unittest
import mongomock
import json
from bookstore import bookstore_api

class BookStoreUnitTests(unittest.TestCase):
    
    def setUp(self):
        self.db = mongomock.MongoClient()['bookstore']
        self.db.books.insert_one({'_id': 1, 'title': 'A test book'})
        self.db.books.insert_one({'_id': 2, 'title': 'Another test book'})
        self.db.books.insert_one({'_id': 3, 'title': 'A rare book'})
        self.db.inventory.insert_one({'_id': 1, 'book_id': 1, 'qty': 5})
        self.db.inventory.insert_one({'_id': 2, 'book_id': 2, 'qty': 0})
        self.db.inventory.insert_one({'_id': 3, 'book_id': 3, 'qty': 0})
        self.db.customers.insert_one({'_id': 1, 'name': 'karthik'})
        self.db.customers.insert_one({'_id': 2, 'name': 'muthu'})
        self.db.customers.insert_one({'_id': 3, 'name': 'anis'})
        bookstore_api.place_order(self.db, 1, 1, 2)
        
    def tearDown(self):
        # Cleanup database
        self.db["books"].delete_many({})
        self.db["inventory"].delete_many({})
        self.db["customers"].delete_many({})
        self.db["orders"].delete_many({})

    def test_get_available_books(self):
        books = bookstore_api.get_available_books(self.db)
        self.assertEquals(len(books), 1)

    def test_get_books(self):
        books = bookstore_api.get_books(self.db)
        self.assertEquals(books.count(), 3)

    def test_get_book(self):
        book = bookstore_api.get_book(self.db, 1)
        self.assertEqual(book['_id'], 1)

    def test_get_inventory(self):
        records = bookstore_api.get_inventory(self.db)
        self.assertEquals(records.count(), 3)

    def test_get_customers(self):
        records = bookstore_api.get_customers(self.db)
        self.assertEquals(records.count(), 3)

    def test_get_customer(self):
        customer = bookstore_api.get_customer(self.db, 1)
        self.assertEqual(customer['_id'], 1)

    def test_get_orders(self):
        records = bookstore_api.get_orders(self.db)
        self.assertEquals(records.count(), 1)

    def test_fullfil_order(self):
        for order in bookstore_api.get_orders(self.db):
            bookstore_api.fullfil_order(self.db, order['_id'])
    
if __name__ == '__main__':
    unittest.main()