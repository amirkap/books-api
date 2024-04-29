import traceback
from flask_restful import Resource, reqparse
from utils.gemini import GeminiAPI
from utils.google_api import GoogleAPI
from utils.open_lib_api import OpenLibAPI
from models.books_col import BooksCollection
from models.ratings_col import RatingsCollection

# Parser to extract book fields
post_parser = reqparse.RequestParser()
post_parser.add_argument('title', type=str, required=True, help='Title cannot be blank!')
post_parser.add_argument('ISBN', type=str, required=True, help='ISBN cannot be blank!')
post_parser.add_argument('genre', type=str,
                         choices=('Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other'),
                         required=True,
                         help='Genre must be one of Fiction, Children, Biography, Science, Science Fiction, Fantasy, or Other')

put_parser = post_parser.copy()
put_parser.add_argument('authors', type=str, required=True, help="Authors cannot be blank!")
put_parser.add_argument('publisher', type=str, required=True, help="Publisher cannot be blank!")
put_parser.add_argument('publishedDate', type=str, required=True, help="Published Date cannot be blank!")
put_parser.add_argument('language', type=list, location='json', required=True, help="Languages cannot be blank!")
put_parser.add_argument('summary', type=str, required=True, help="Summary cannot be blank!")


class Books(Resource):
    def get(self, book_id=None):
        if not book_id:
            return {"message": "Books retrieved successfully.", "books": BooksCollection.get_all_books()}, 200
        try:
            book = BooksCollection.find_book(book_id)
            if book:
                return {"message": "Book retrieved successfully.", "book": book}, 200
            else:
                return {"message": "Book not found.", "id": book_id}, 404
        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
            return {"message": "Internal server error, try later."}, 500

    def post(self):
            args = dict(post_parser.parse_args())
            if BooksCollection.find_book_by_isbn(args['ISBN']):
                return {"message": "Book already exists."}, 422

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
                args["summary"] = "missing"

            book_id = BooksCollection.insert_book(args)
            rating = RatingsCollection.insert_rating(book_id, args['title'])
            return {"message": "Book created successfully.", "book": book_id}, 201

    def put(self, book_id):
        args = dict(put_parser.parse_args())
        if BooksCollection.find_book(book_id):
            args['id'] = book_id
            book_data = BooksCollection.insert_book(args, update=True)
            return {"message": "Book updated successfully.", "book": book_data}, 200
        else:
            return {"message": "Book not found.", "id": book_id}, 404

    def delete(self, book_id):
        try:
            if BooksCollection.delete_book(book_id):
                RatingsCollection.delete_rating(book_id)
                return {"message": "Book deleted successfully.", "id": book_id}, 200
            else:
                return {"message": "Book not found.", "id": book_id}, 404
        except Exception as e:
            return {"message": "Internal server error, try later."}, 500
