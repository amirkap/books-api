import traceback
from flask import request
from flask_restful import Resource, reqparse, abort
from models.ratings_col import RatingsCollection

class Ratings(Resource):
    def get(self, book_id=None):
        book_id = book_id or request.args.get('id')

        if not book_id:
            return RatingsCollection.get_all_ratings(), 200
        try:
            rating = RatingsCollection.find_rating(book_id)
            if rating:
                return rating, 200
            else:
                return {"message": "Rating not found.", "id": book_id}, 404
        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
            return {"message": "Internal server error, try later."}, 500


class RatingValues(Resource):
    def post(self, book_id):
        # Check for correct content type
        if not request.is_json:
            abort(415, message="Unsupported media type: Expected application/json")

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('value', type=int, required=True, choices=[1, 2, 3, 4, 5],
                            help="Value must be an integer and between 1 to 5!")
        try:
            args = parser.parse_args()
        except Exception as e:
            error_messages = e.data if hasattr(e, 'data') else str(e)
            error_messages = error_messages.get('message') if isinstance(error_messages, dict) else error_messages
            abort(422, message=error_messages)

        new_average = RatingsCollection.add_value_to_rating(book_id, args['value'])
        if new_average is None:
            return {"message": "Book id not found.", "id": book_id}, 404

        return {'average_rating': new_average}, 201

class RatingsTop(Resource):
    def get(self):
        top_ratings = RatingsCollection.get_top_ratings()
        return [{
                'id': rating['id'],
                'title': rating['title'],
                'average': rating['average']
            } for rating in top_ratings], 200