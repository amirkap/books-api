from flask import Flask
from flask_restful import Api
from resources.loans import Loans

app = Flask(__name__)
api = Api(app)

api.add_resource(Loans, '/loans', '/loans/<string:loan_id>')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5002)
