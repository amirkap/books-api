from pymongo import MongoClient
from bson.objectid import ObjectId


class BooksCollection:
    def __init__(self, mongo_url):
        self.client = MongoClient(mongo_url)
        self.db = self.client.booksdb  # This sets the database name
        self.books = self.db.books  # This sets the collection name

    def insert_book(self, book_data, update=False):
        if update:
            book_id = book_data['id']
            self.books.update_one({"_id": ObjectId(book_id)}, {"$set": book_data})
        else:
            result = self.books.insert_one(book_data)
            book_id = str(result.inserted_id)
            self.books.update_one({"_id": result.inserted_id}, {"$set": {"id": book_id}})  # We want regular ID too
        return book_id

    def delete_book(self, book_id):
        result = self.books.delete_one({"_id": ObjectId(book_id)})
        return result.deleted_count > 0

    def find_book(self, book_id):
        book = self.books.find_one({"_id": ObjectId(book_id)})
        if book:
            book.pop("_id", None)
        return book

    def find_book_by_isbn(self, isbn):
        book = self.books.find_one({"ISBN": isbn})
        if book:
            book.pop("_id", None)
        return book

    def get_all_books(self):
        books = list(self.books.find())
        for book in books:
            book.pop("_id", None)
        return books

    def filter_books_by_criteria(self, criteria):
        if "summary" in criteria:
            del criteria["summary"]
        books = list(self.books.find(criteria))
        for book in books:
            book.pop("_id", None)
        return books
