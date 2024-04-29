import traceback
from flask_restful import Resource, reqparse
from models.ratings_col import RatingsCollection

class Ratings(Resource):
    def get(self, book_id=None):
        if not book_id:
            return {"message": "Ratings retrieved successfully.", "ratings": RatingsCollection.get_all_ratings()}, 200
        try:
            rating = RatingsCollection.find_rating(book_id)
            if rating:
                return {"message": "Rating retrieved successfully.", "rating": rating}, 200
            else:
                return {"message": "Rating not found.", "id": book_id}, 404
        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
            return {"message": "Internal server error, try later."}, 500


class RatingValues(Resource):
    def post(self, book_id):
        parser = reqparse.RequestParser()
        parser.add_argument('value', type=int, required=True, choices=[1, 2, 3, 4, 5],
                            help="Value must be an integer and between 1 to 5!")
        args = parser.parse_args()
        new_average = RatingsCollection.add_value_to_rating(book_id, args['value'])
        if new_average is None:
            return {"message": "Rating not found.", "id": book_id}, 404

        return {'message': "New rating value added successfully", 'id': book_id, 'average_rating': new_average}, 201

class RatingsTop(Resource):
    def get(self):
        top_ratings = RatingsCollection.get_top_ratings()
        print(top_ratings)
        return {
            "message": "Top ratings retrieved successfully.",
            "top": [{
                'id': rating['id'],
                'title': rating['title'],
                'average': rating['average']
            } for rating in top_ratings]
        }, 200