import traceback

from flask import Flask
from flask_restful import Resource, Api, reqparse

from google_api import GoogleAPI
from models.books_col import BooksCollection
from open_lib_api import OpenLibAPI

app = Flask(__name__)
api = Api(app)
books_collection = BooksCollection()  # Instance of BooksCollection

# Parser to extract book fields
books_parser = reqparse.RequestParser()
books_parser.add_argument('title', type=str, required=True, help='Title cannot be blank!')
books_parser.add_argument('ISBN', type=str, required=True, help='ISBN cannot be blank!')
books_parser.add_argument('genre', type=str,
                          choices=('Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other'),
                          required=True,
                          help='Genre must be one of Fiction, Children, Biography, Science, Science Fiction, Fantasy, or Other')

class Book(Resource):
    def get(self, book_id):
        try:
            book = books_collection.find_book(book_id)
            if book:
                return {"message": "Book retrieved successfully.", "book": book}, 200
            else:
                return {"message": "Book not found.", "id": book_id}, 404
        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
            return {"message": "Internal server error, try later."}, 500

    def post(self):
            args = dict(books_parser.parse_args())
            # get book data from Google API
            google_api = GoogleAPI()
            open_lib_api = OpenLibAPI()
            book_data_google_response = google_api.get_book_language(args['ISBN'])

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
            book_data = books_collection.insert_book(args)
            return {"message": "Book created successfully.", "book": book_data}, 201

    def delete(self, book_id):
        try:
            if books_collection.delete_book(book_id):
                return {"message": "Book deleted successfully.", "id": book_id}, 200
            else:
                return {"message": "Book not found.", "id": book_id}, 404
        except Exception as e:
            return {"message": "Internal server error, try later."}, 500


api.add_resource(Book, '/book', '/book/<string:book_id>')

if __name__ == '__main__':
    app.run(debug=True)
