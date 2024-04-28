from google_api import GoogleAPI

class BooksCollection:
    def __init__(self):
        self.books = {}
        self.current_id = 1

    def insert_book(self, book_data, update=False):
        """Insert a new book and return its ID."""
        if update:
            book_id = book_data['id']
        else:
            book_id = str(self.current_id)
            self.current_id += 1

        self.books[book_id] = {
            "title": book_data['title'],
            "authors": book_data['authors'],
            "ISBN": book_data['ISBN'],
            "genre": book_data['genre'],
            "publisher": book_data['publisher'],
            "publishedDate": book_data['publishedDate'],
            "language": book_data['language'],
            "summary": book_data['summary'],
            "id": book_id
        }
        return book_id

    def delete_book(self, book_id):
        """Delete a book by ID."""
        if book_id in self.books:
            del self.books[book_id]
            return True
        return False

    def find_book(self, book_id):
        """Find a book by ID."""
        return self.books.get(book_id)

    def find_book_by_isbn(self, isbn):
        """Find a book by ISBN."""
        for book in self.books.values():
            if book['ISBN'] == isbn:
                return book
        return None

    def get_all_books(self):
        """Return all books."""
        return list(self.books.values())
