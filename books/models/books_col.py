from pymongo import MongoClient
from bson.objectid import ObjectId


class BooksCollection:
    def __init__(self, mongo_url):
        self.client = MongoClient(mongo_url)
        self.db = self.client.booksdb  # This sets the database name
        self.books = self.db.books  # This sets the collection name

    def insert_book(self, book_data, update=False):
        if update:
            book_id = book_data['_id']
            self.books.update_one({"_id": ObjectId(book_id)}, {"$set": book_data})
            return book_id
        else:
            result = self.books.insert_one(book_data)
            return str(result.inserted_id)

    def delete_book(self, book_id):
        result = self.books.delete_one({"_id": ObjectId(book_id)})
        return result.deleted_count > 0

    def find_book(self, book_id):
        return self.books.find_one({"_id": ObjectId(book_id)})

    def find_book_by_isbn(self, isbn):
        return self.books.find_one({"ISBN": isbn})

    def get_all_books(self):
        return list(self.books.find())

    def filter_books_by_criteria(self, criteria):
        if "summary" in criteria:
            del criteria["summary"]
        return list(self.books.find(criteria))
