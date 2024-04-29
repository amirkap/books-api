import requests


class OpenLibAPI:
    def get_language(self, isbn):
        url = f"https://openlibrary.org/search.json?q={isbn}&fields=language"
        try:
            response = requests.get(url)
        except Exception as e:
            print(f"Error: {e}")
            return {"error": "Unable to connect to OpenLibrary API."}, 500

        data = response.json()
        try:
            if not data['docs']:
                return {"error": "No books found for the provided ISBN."}, 400
            if 'language' not in data['docs'][0]:
                return {"error": "No language found for the provided ISBN."}, 400

            language = data['docs'][0]['language']
            return {"language": language}, 200
        except (IndexError, KeyError) as e:
            return {"error": f"Data parsing error: {e}"}, 500