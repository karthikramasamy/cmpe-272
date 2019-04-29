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
        
    def tearDown(self):
        # Cleanup database
        self.db["books"].delete_many({})
        self.db["inventory"].delete_many({})
        self.db["customers"].delete_many({})
        self.db["orders"].delete_many({})

    def test_get_book(self):
        book = bookstore.get_book(self.db, 1)
        self.assertEqual(book['_id'], 1)

    def test_get_books(self):
        books = bookstore.get_books(self.db)
        self.assertEquals(books.count(), 3)

    def test_get_available_books(self):
        books = bookstore.get_available_books(self.db)
        self.assertEquals(len(books), 1)

if __name__ == '__main__':
    unittest.main()