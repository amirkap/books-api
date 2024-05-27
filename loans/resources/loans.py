import os
import traceback
import requests
from flask import request, jsonify
from flask_restful import Resource, reqparse, abort
from ..models.loans_col import LoansCollection


class Loans(Resource):
    def __init__(self):
        self.loans_collection = LoansCollection(request.environ['MONGO_URL'])
        self.books_service_url = os.getenv('BOOKS_SERVICE_URL')


    def get(self, loan_id=None):
        if not loan_id:
            if request.args:
                filters = {key: request.args[key] for key in request.args}
                loans = self.loans_collection.get_all_loans()
                filtered_loans = [loan for loan in loans if all(loan.get(k) == v for k, v in filters.items())]
                return jsonify(filtered_loans)
            return self.loans_collection.get_all_loans(), 200

        try:
            loan = self.loans_collection.find_loan(loan_id)
            if loan:
                return loan, 200
            else:
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
        args = parser.parse_args()

        # Retrieve book details from the books service
        book_response = requests.get(f'{self.books_service_url}/books?ISBN={args["ISBN"]}')
        if book_response.status_code != 200:
            return {"message": "Book not found in books service.", "ISBN": args["ISBN"]}, 422

        books_data = book_response.json()

        # Check if any of the books with the given ISBN is available
        on_loan_books = self.loans_collection.find_loans_by_isbn(args["ISBN"])
        available_books = [book for book in books_data if book['id'] not in [loan['bookID'] for loan in on_loan_books]]

        if not available_books:
            return {"message": "All copies of this book are currently on loan.", "ISBN": args["ISBN"]}, 422

        # Check if the member already has 2 or more books on loan
        member_loans = self.loans_collection.find_loans_by_member(args["memberName"])
        if len(member_loans) >= 2:
            return {"message": "Member already has 2 or more books on loan.", "memberName": args["memberName"]}, 422

        # Use the first available book for the loan
        book_data = available_books[0]
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
        except Exception as e:
            return {"message": "Internal server error, try later."}, 500
