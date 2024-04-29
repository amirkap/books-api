from flask import Flask
from flask_restful import Api
from resources.books import Books
from resources.ratings import Ratings, RatingValues, RatingsTop

# Create a Flask app
app = Flask(__name__)

# Create a Flask-RESTful API
api = Api(app)

# Add resources to the API
api.add_resource(Books, '/books', '/books/<string:book_id>')
api.add_resource(Ratings, '/ratings', '/ratings/<string:book_id>')
api.add_resource(RatingValues, '/ratings/<string:book_id>/values')
api.add_resource(RatingsTop, '/top')


if __name__ == '__main__':
    app.run(port=8000, debug=False)