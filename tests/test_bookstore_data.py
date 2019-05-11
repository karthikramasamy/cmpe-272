import unittest
import mongomock
import json
import datetime
from bookstore import bookstore_data


class BookStoreUnitTests(unittest.TestCase):

    def setUp(self):
        self.db = mongomock.MongoClient()['bookstore']
        self.db.books.insert_many(
            [{
                "_id": "0123456789ab012345678901",
                "title": "Becoming",
                "author": ["Michelle Obama"],
                "language": "English",
                "isbn": "1524763136",
                "published_date": "2018-11-13",
                "publisher": "Crown Publishing Group"
            }, {
                "_id": "0123456789ab012345678902",
                "title": "Redemption",
                "author": ["David Baldacci"],
                "language": "English",
                "isbn": "1538761459",
                "published_date": "2019-10-08",
                "publisher": "Grand Central Publishing"
            }, {
                "_id": "0123456789ab012345678903",
                "title": "Milkman: A Novel",
                "author": ["Anna Burns"],
                "language": "English",
                "isbn": "1644450003",
                "published_date": "2018-12-04",
                "publisher": "Graywolf Press"
            }]
        )

        # Insert sample data for inventory
        self.db.inventory.insert_many(
            [{
                "book_id": "0123456789ab012345678901",
                "qty": 5,
                "last_modified": datetime.datetime.utcnow()
            }, {
                "book_id": "0123456789ab012345678902",
                "qty": 0,
                "last_modified": datetime.datetime.utcnow()
            }, {
                "book_id": "0123456789ab012345678903",
                "qty": 0,
                "last_modified": datetime.datetime.utcnow()
            }]
        )

        # Insert sample data for customers
        self.db.customers.insert_many(
            [{
                "_id": "0123456789ab012345678901",
                "name": "Karthik",
                "address": "San Jose, CA",
                "phone": "408-000-001",
                "last_modified": datetime.datetime.utcnow()
            }, {
                "_id": "0123456789ab012345678902",
                "name": "Muthu",
                "address": "San Jose, CA",
                "phone": "408-000-002",
                "last_modified": datetime.datetime.utcnow()
            }, {
                "_id": "0123456789ab012345678903",
                "name": "Anis",
                "address": "San Jose, CA",
                "phone": "408-000-003",
                "last_modified": datetime.datetime.utcnow()
            }]
        )
        bookstore_data.place_order(self.db, "0123456789ab012345678901", [{"book_id": "0123456789ab012345678901", "qty": 2}])

    def tearDown(self):
        # Cleanup database
        self.db["books"].delete_many({})
        self.db["inventory"].delete_many({})
        self.db["customers"].delete_many({})
        self.db["orders"].delete_many({})

    def test_get_all_books(self):
        books = bookstore_data.get_all_books(self.db)
        self.assertIsNotNone(books)
        self.assertEquals(len(books), 3)

    def test_get_available_books(self):
        books = bookstore_data.get_available_books(self.db)
        self.assertIsNotNone(books)
        self.assertEquals(len(books), 1)

    def test_get_book_by_isbn(self):
        book = bookstore_data.get_book_by_isbn(self.db, '1524763136')
        self.assertIsNotNone(book)
        self.assertEqual(book['isbn'], '1524763136')

    def test_get_book_by_id(self):
        book = bookstore_data.get_book_by_id(self.db, '0123456789ab012345678901')
        self.assertIsNotNone(book)
        self.assertEqual(book['_id'], '0123456789ab012345678901')

    def test_get_inventory_quantity_by_book_id(self):
        qty = bookstore_data.get_inventory_quantity_by_book_id(self.db, '0123456789ab012345678901')
        self.assertEquals(qty, 5)

    def test_get_customers(self):
        customers = bookstore_data.get_customers(self.db)
        self.assertIsNotNone(customers)
        self.assertEquals(len(customers), 3)

    def test_get_customer_by_id(self):
        customer = bookstore_data.get_customer_by_id(self.db, '0123456789ab012345678901')
        self.assertIsNotNone(customer)
        self.assertEqual(customer['_id'], '0123456789ab012345678901')

    def test_get_orders(self):
        orders = bookstore_data.get_orders(self.db)
        self.assertIsNotNone(orders)
        self.assertGreaterEqual(len(orders), 1)

    def test_get_order_by_id(self):
        placed_order = bookstore_data.place_order(self.db, "0123456789ab012345678901", [{"book_id": "0123456789ab012345678901", "qty": 2}])
        self.assertIsNotNone(placed_order)
        order = bookstore_data.get_order_by_id(self.db, placed_order['_id'])
        self.assertIsNotNone(order)
        self.assertEquals(order['_id'], placed_order['_id'])

    def test_fulfill_order(self):
       orders = bookstore_data.get_orders(self.db)
       for order in orders:
           bookstore_data.fulfill_order(self.db, order['_id'])


if __name__ == '__main__':
    unittest.main()
