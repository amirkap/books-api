import os
import traceback
import json
from flask import request
from flask_restful import Resource, abort
from bson import json_util
from utils.google_api import GoogleAPI
from models.books_col import BooksCollection
from models.ratings_col import RatingsCollection
from utils.validation_utils import get_put_parser, get_post_parser

class Books(Resource):
    def __init__(self):
        self.books_collection = BooksCollection(os.environ['MONGO_URL'])
        self.ratings_collection = RatingsCollection(os.environ['MONGO_URL'])

    def get(self, book_id=None):
        if not book_id:
            if request.args:
                filters = {key: request.args[key] for key in request.args}
                filtered_books = self.books_collection.filter_books_by_criteria(filters)
                json_books = json.loads(json_util.dumps(filtered_books))
                return json_books, 200
            else:
                json_books = json.loads(json_util.dumps(self.books_collection.get_all_books()))
                return json_books, 200

        try:
            book = self.books_collection.find_book(book_id)
            if book:
                json_book = json.loads(json_util.dumps(book))
                return json_book, 200
            else:
                return {"message": "Book not found.", "id": book_id}, 404
        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
            return {"message": "Internal server error, try later."}, 500

    def post(self):
        if not request.is_json:
            abort(415, message="Unsupported media type: Expected application/json")

        try:
            post_parser = get_post_parser()
            args = dict(post_parser.parse_args())
        except Exception as e:
            error_messages = e.data if hasattr(e, 'data') else str(e)
            error_messages = error_messages.get('message') if isinstance(error_messages, dict) else error_messages
            abort(422, message=error_messages)

        if self.books_collection.find_book_by_isbn(args['ISBN']):
            abort(422, message="Book with the same ISBN already exists.")

        google_api = GoogleAPI()
        book_data_google_response = google_api.get_book_details(args['ISBN'])

        if book_data_google_response[1] != 200:
            response = book_data_google_response
            return response[0], response[1]

        google_data = book_data_google_response[0]
        args.update({**google_data})

        book_id = self.books_collection.insert_book(args)
        self.ratings_collection.insert_rating(book_id, args['title'])
        return {"id": book_id}, 201

    def put(self, book_id):
        if not request.is_json:
            abort(415, message="Unsupported media type: Expected application/json")

        try:
            put_parser = get_put_parser()
            args = dict(put_parser.parse_args())
        except Exception as e:
            error_messages = e.data if hasattr(e, 'data') else str(e)
            error_messages = error_messages.get('message') if isinstance(error_messages, dict) else error_messages
            abort(422, message=error_messages)

        if self.books_collection.find_book(book_id):
            args['id'] = book_id
            self.books_collection.insert_book(args, update=True)
            self.ratings_collection.update_book_title(book_id, args['title'])
            return {"id": book_id}, 200
        else:
            return {"message": "Book not found.", "id": book_id}, 404

    def delete(self, book_id):
        try:
            if self.books_collection.delete_book(book_id):
                self.ratings_collection.delete_rating(book_id)
                return {"id": book_id}, 200
            else:
                return {"message": "Book not found.", "id": book_id}, 404
        except Exception as e:
            return {"message": "Internal server error, try later."}, 500
