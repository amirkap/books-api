import os
import traceback
import requests
import json
from bson.errors import InvalidId
from flask import request
from flask_restful import Resource, reqparse, abort
from bson import json_util
from models.loans_col import LoansCollection


class Loans(Resource):
    def __init__(self):
        self.loans_collection = LoansCollection(os.getenv('MONGO_URL'))
        self.books_service_url = os.getenv('BOOKS_SERVICE_URL')


    def get(self, loan_id=None):
        if not loan_id:
            if request.args:
                filters = {key: request.args[key] for key in request.args}
                loans = self.loans_collection.get_all_loans()
                filtered_loans = [loan for loan in loans if all(loan.get(k) == v for k, v in filters.items())]
                json_loans = json.loads(json_util.dumps(filtered_loans))
                return json_loans, 200
            json_loans = json.loads(json_util.dumps(self.loans_collection.get_all_loans()))
            return json_loans, 200

        try:
            loan = self.loans_collection.find_loan(loan_id)
            if loan:
                json_loan = json.loads(json_util.dumps(loan))
                return json_loan, 200
            else:
                return {"message": "Loan not found.", "loanID": loan_id}, 404
        except InvalidId as e:
            return {"message": "Loan not found.", "loanID": loan_id}, 404
        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
            return {"message": "Internal server error, try later."}, 500

    def post(self):
        if not request.is_json:
            abort(415, message="Unsupported media type: Expected application/json")

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('memberName', type=str, required=True, help="Member name is required")
        parser.add_argument('ISBN', type=str, required=True, help="ISBN is required")
        parser.add_argument('loanDate', type=str, required=True, help="Loan date is required")

        try:
            args = parser.parse_args()
        except Exception as e:
            error_messages = e.data if hasattr(e, 'data') else str(e)
            error_messages = error_messages.get('message') if isinstance(error_messages, dict) else error_messages
            abort(422, message=error_messages)

        # Retrieve book details from the books service
        book_response = requests.get(f'{self.books_service_url}/books?ISBN={args["ISBN"]}')
        if book_response.status_code != 200:
            return {"message": "Book not found in books service.", "ISBN": args["ISBN"]}, 422

        books_data = list(book_response.json())

        if not books_data:
            return {"message": "Book not found in books service.", "ISBN": args["ISBN"]}, 422

        book_data = books_data[0]  # Assume only one book per ISBN

        # Check if any of the books with the given ISBN is available
        on_loan_books = self.loans_collection.find_loans_by_isbn(args["ISBN"])
        if on_loan_books:
            return {"message": "This book is currently on loan.", "ISBN": args["ISBN"]}, 422

        # Check if the member already has 2 or more books on loan
        member_loans = self.loans_collection.find_loans_by_member(args["memberName"])
        if len(member_loans) >= 2:
            return {"message": "Member already has 2 or more books on loan.", "memberName": args["memberName"]}, 422

        loan_data = {
            "memberName": args["memberName"],
            "ISBN": args["ISBN"],
            "loanDate": args["loanDate"],
            "title": book_data["title"],
            "bookID": book_data["id"]
        }

        # Insert loan data into the database and let MongoDB generate the _id
        loan_id = self.loans_collection.insert_loan(loan_data)
        return {"loanID": loan_id}, 201

    def delete(self, loan_id):
        try:
            if self.loans_collection.delete_loan(loan_id):
                return {"loanID": loan_id}, 200
            else:
                return {"message": "Loan not found.", "loanID": loan_id}, 404
        except InvalidId as e:
            return {"message": "Loan not found.", "loanID": loan_id}, 404
        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
            return {"message": "Internal server error, try later."}, 500
