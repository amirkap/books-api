from pymongo import MongoClient
from bson.objectid import ObjectId


class LoansCollection:
    def __init__(self, mongo_url):
        self.client = MongoClient(mongo_url)
        self.db = self.client.loansdb  # This sets the database name
        self.loans = self.db.loans  # This sets the collection name

    def insert_loan(self, loan_data):
        result = self.loans.insert_one(loan_data)
        loan_id = result.inserted_id
        self.loans.update_one({"_id": loan_id}, {"$set": {"loanID": str(loan_id)}})
        return str(loan_id)

    def delete_loan(self, loan_id):
        result = self.loans.delete_one({"_id": ObjectId(loan_id)})
        return result.deleted_count > 0

    def find_loan(self, loan_id):
        return self.loans.find_one({"_id": ObjectId(loan_id)})

    def find_loans_by_member(self, member_name):
        return list(self.loans.find({"memberName": member_name}))

    def find_loans_by_isbn(self, isbn):
        return list(self.loans.find({"ISBN": isbn}))

    def get_all_loans(self):
        return list(self.loans.find())
