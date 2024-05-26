from pymongo import MongoClient

class RatingsCollection:
    def __init__(self, mongo_url):
        self.client = MongoClient(mongo_url)
        self.db = self.client.booksdb  # This sets the database name
        self.ratings = self.db.ratings # This sets the collection name

    def insert_rating(self, book_id, book_title):
        if not self.find_rating(book_id):
            self.ratings.insert_one({
                "book_id": book_id,
                "title": book_title,
                "values": [],
                "average": 0
            })

    def add_value_to_rating(self, book_id, value):
        rating = self.find_rating(book_id)
        if rating:
            values = rating['values']
            values.append(value)
            new_avg = sum(values) / len(values)
            self.ratings.update_one({"book_id": book_id}, {"$set": {"values": values, "average": new_avg}})
            return new_avg
        return None

    def find_rating(self, book_id):
        return self.ratings.find_one({"book_id": book_id})

    def get_all_ratings(self):
        return list(self.ratings.find())

    def delete_rating(self, book_id):
        result = self.ratings.delete_one({"book_id": book_id})
        return result.deleted_count > 0

    def update_book_title(self, book_id, new_title):
        result = self.ratings.update_one({"book_id": book_id}, {"$set": {"title": new_title}})
        return result.modified_count > 0

    def get_top_ratings(self):
        ratings = self.get_all_ratings()
        if not ratings:
            return []

        at_least_three_ratings = [r for r in ratings if len(r['values']) >= 3]
        if not at_least_three_ratings:
            return []

        sorted_ratings = sorted(at_least_three_ratings, key=lambda x: x['average'], reverse=True)
        top_scores = sorted(list(set([rating['average'] for rating in sorted_ratings])), reverse=True)[:3]
        top_ratings = [rating for rating in sorted_ratings if rating['average'] in top_scores]

        return top_ratings
