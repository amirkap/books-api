from flask import Flask
from flask_restful import Api
from resources.books import Books
from resources.ratings import Ratings, RatingValues, RatingsTop

app = Flask(__name__)
api = Api(app)

api.add_resource(Books, '/books', '/books/<string:book_id>')
api.add_resource(Ratings, '/ratings', '/ratings/<string:book_id>')
api.add_resource(RatingValues, '/ratings/<string:book_id>/values')
api.add_resource(RatingsTop, '/top')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
