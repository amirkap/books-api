class RatingsCollection:
    ratings = {}

    @staticmethod
    def insert_rating(book_id, book_title):
        """Insert a new rating for a book if it does not already exist."""
        if book_id not in RatingsCollection.ratings:
            RatingsCollection.ratings[book_id] = {
                "values": [],
                "average": 0,
                "title": book_title,
                "id": book_id
            }

    @staticmethod
    def add_value_to_rating(book_id, value):
        """Add a new value to the existing rating for a book and update the average."""
        if book_id in RatingsCollection.ratings:
            RatingsCollection.ratings[book_id]["values"].append(value)
            new_avg = round(sum(RatingsCollection.ratings[book_id]["values"]) / len(RatingsCollection.ratings[book_id]["values"]), 2)
            RatingsCollection.ratings[book_id]["average"] = new_avg
            return new_avg
        else:
            return None

    @staticmethod
    def find_rating(book_id):
        """Find a rating by book ID."""
        return RatingsCollection.ratings.get(book_id)
    @staticmethod
    def get_all_ratings():
        """Return all ratings."""
        return list(RatingsCollection.ratings.values())

    @staticmethod
    def delete_rating(book_id):
        """Delete a rating by book ID."""
        if book_id in RatingsCollection.ratings:
            del RatingsCollection.ratings[book_id]
            return True
        return False

    @staticmethod
    def update_book_title(book_id, new_title):
        """Update a rating by book ID."""
        if book_id in RatingsCollection.ratings:
            RatingsCollection.ratings[book_id]["title"] = new_title
            return True
        return False

    @staticmethod
    def get_top_ratings():
        """Return top ratings."""
        # Retrieve all ratings from the collection
        ratings = RatingsCollection.get_all_ratings()

        # Check if there are any ratings
        if not ratings:
            return []

        # Filter out books with less than three ratings
        at_least_three_ratings = list(filter(lambda x: len(x['values']) >= 3, ratings))

        # Check if there are any books with at least three ratings
        if not at_least_three_ratings:
            return []

        # Sort the books by their average score, in descending order
        sorted_ratings = sorted(at_least_three_ratings, key=lambda x: x['average'], reverse=True)

        # Get the top 3 scores
        top_scores = sorted(list(set([rating['average'] for rating in sorted_ratings])), reverse=True)[:3]

        # Collect all books that have the top 3 scores
        top_ratings = [rating for rating in sorted_ratings if rating['average'] in top_scores]

        return top_ratings
