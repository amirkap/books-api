import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class GeminiAPI:
    """
    A class to interact with the Google Generative AI model.
    """
    def __init__(self, api_key=None, model_name='gemini-pro'):
        """
        Initializes the GeminiAPI with an API key and model name.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided during class initialization or set in the environment.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def get_response(self, prompt):
        """
        Generates content based on the provided prompt.
        """
        try:
            response = self.model.generate_content(prompt)
        except Exception as e:
            print(f"Error: {e}")
            return None
        return response.text

# Example usage
if __name__ == "__main__":
    gemini = GeminiAPI()
    print(gemini.get_response("Summarize the book Harry Potter and the Philosopher's Stone by J. K. Rowling in 5 sentences or less."))
