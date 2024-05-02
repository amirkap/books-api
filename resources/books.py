import traceback
from flask import request
from flask_restful import Resource, reqparse, abort
from utils.gemini import GeminiAPI
from utils.google_api import GoogleAPI
from utils.open_lib_api import OpenLibAPI
from models.books_col import BooksCollection
from models.ratings_col import RatingsCollection
from utils.validation_utils import get_put_parser, get_post_parser

class Books(Resource):
    def get(self, book_id=None):
        if not book_id:
            # Check if there are query parameters for filtering
            if request.args:
                # Create a filter dictionary from query parameters
                filters = {key: request.args[key] for key in request.args}
                filtered_books = BooksCollection.filter_books_by_criteria(filters)
                return filtered_books, 200
            else:
                # No query parameters, return all books
                return BooksCollection.get_all_books(), 200

        try:
            book = BooksCollection.find_book(book_id)
            if book:
                return book, 200
            else:
                return {"message": "Book not found.", "id": book_id}, 404
        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
            return {"message": "Internal server error, try later."}, 500

    def post(self):
        # Check for correct content type
        if not request.is_json:
            abort(415, message="Unsupported media type: Expected application/json")

        try:
            post_parser = get_post_parser()
            args = dict(post_parser.parse_args())
        except Exception as e:
            error_messages = e.data if hasattr(e, 'data') else str(e)
            error_messages = error_messages.get('message') if isinstance(error_messages, dict) else error_messages
            abort(422, message=error_messages)

        if BooksCollection.find_book_by_isbn(args['ISBN']):
            abort(422, message="Book with the same ISBN already exists.")

        # get book data from Google API
        google_api = GoogleAPI()
        open_lib_api = OpenLibAPI()
        book_data_google_response = google_api.get_book_details(args['ISBN'])

        if book_data_google_response[1] != 200:
            response = book_data_google_response
            return response[0], response[1]

        open_lib_api_response = open_lib_api.get_language(args['ISBN'])

        if open_lib_api_response[1] != 200:
            response = open_lib_api_response
            return response[0], response[1]

        google_data = book_data_google_response[0]
        open_lib_data = open_lib_api_response[0]
        args.update({**google_data, **open_lib_data})

        # add summary of the book
        try:
            prompt = f"Summarize the book {args['title']} by {args['authors']} in 5 sentences or less."
            gemini = GeminiAPI()
            gemini_response = gemini.get_response(prompt)
            if not gemini_response:
                args["summary"] = "missing"
            args["summary"] = gemini_response
        except Exception as e:
            print(f"Error: {e}")
            abort(500, message="Unable to connect to Gemini.")

        book_id = BooksCollection.insert_book(args)
        rating = RatingsCollection.insert_rating(book_id, args['title'])
        return {"id": book_id}, 201

    def put(self, book_id):
        # Check for correct content type
        if not request.is_json:
            abort(415, message="Unsupported media type: Expected application/json")

        try:
            put_parser = get_put_parser()
            args = dict(put_parser.parse_args())
        except Exception as e:
            error_messages = e.data if hasattr(e, 'data') else str(e)
            error_messages = error_messages.get('message') if isinstance(error_messages, dict) else error_messages
            abort(422, message=error_messages)

        if BooksCollection.find_book(book_id):
            args['id'] = book_id
            book_data = BooksCollection.insert_book(args, update=True)
            rating = RatingsCollection.update_book_title(book_id, args['title'])
            return {"id": book_id}, 200
        else:
            return {"message": "Book not found.", "id": book_id}, 404

    def delete(self, book_id):
        try:
            if BooksCollection.delete_book(book_id):
                RatingsCollection.delete_rating(book_id)
                return {"id": book_id}, 200
            else:
                return {"message": "Book not found.", "id": book_id}, 404
        except Exception as e:
            return {"message": "Internal server error, try later."}, 500
