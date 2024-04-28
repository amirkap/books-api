import requests

class GoogleAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_book_language(self, isbn):
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

        try:
            response = requests.get(url)
            print(response.json())
            total_items = response.json()["totalItems"]
            if total_items == 0:
                return {"error": "No books found for the provided ISBN."}, 400

        except Exception as e:
            print(f"Error: {e}")
            return {"error": "No books found for the provided ISBN."}, 400

        books_data = response.json()["items"][0]["volumeInfo"]

        book = {
            "authors": " and ".join(books_data["authors"]) if books_data["authors"] else "missing",
            "publisher": books_data.get("publisher", "missing"),
            "publishedDate": books_data.get("publishedDate", "missing"),
        }

        return book, 200