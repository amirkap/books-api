import requests


class OpenLibAPI:
    def get_language(self, isbn):
        url = f"https://openlibrary.org/search.json?q={isbn}&fields=key,title,author_name,language"
        try:
            response = requests.get(url)
        except Exception as e:
            print(f"Error: {e}")
            return {"error": "Failed to fetch data from OpenLibrary API."}, 400

        data = response.json()
        try:
            if not data['docs']:
                return {"error": "No books found for the provided ISBN."}, 400
            if 'language' not in data['docs'][0]:
                return {"error": "No language found for the provided ISBN."}, 400

            language = data['docs'][0]['language']
            return {"language": language}, 200
        except (IndexError, KeyError) as e:
            raise Exception(f"Data parsing error: {e}")
