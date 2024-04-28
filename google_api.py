import requests
from flask import jsonify


class GoogleAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_book(self, isbn):
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

        try:
            response = requests.get(url)
            books_data = response.json()["items"][0]["volumeInfo"]
            total_items = response.json()["totalItems"]
        except Exception as e:
            print(f"Error: {e}")
            return None
        if total_items == 0:
            return jsonify({"error": "No books found for the provided ISBN."}, 400)

        book = {
            "authors": " and ".join(books_data["authors"]) if books_data["authors"] else "missing",
            "publisher": books_data.get("publisher", "missing"),
            "publishedDate": books_data.get("publishedDate", "missing"),
        }

        return jsonify(book, 200)