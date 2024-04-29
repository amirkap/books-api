class BooksCollection:
    books = {}
    current_id = 1

    @staticmethod
    def insert_book(book_data, update=False):
        """Insert a new book and return its ID."""
        if update:
            book_id = book_data['id']
        else:
            book_id = str(BooksCollection.current_id)
            BooksCollection.current_id += 1

        BooksCollection.books[book_id] = {
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

    @staticmethod
    def delete_book(book_id):
        """Delete a book by ID."""
        if book_id in BooksCollection.books:
            del BooksCollection.books[book_id]
            return True
        return False

    @staticmethod
    def find_book(book_id):
        """Find a book by ID."""
        return BooksCollection.books.get(book_id)

    @staticmethod
    def find_book_by_isbn(isbn):
        """Find a book by ISBN."""
        for book in BooksCollection.books.values():
            if book['ISBN'] == isbn:
                return book
        return None

    @staticmethod
    def get_all_books():
        """Return all books."""
        return list(BooksCollection.books.values())

    @staticmethod
    def filter_books_by_criteria(criteria):
        """Filter books by criteria."""
        if "summary" in criteria:
            del criteria["summary"]

        filtered_books = []
        for book in BooksCollection.books.values():
            match = True
            for key, value in criteria.items():
                if key == 'language':
                    if value not in book.get(key, []):
                        match = False
                        break
                else:
                    if book.get(key) != value:
                        match = False
                        break
            if match:
                filtered_books.append(book)

        return filtered_books
