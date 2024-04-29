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

        try:
            response_text = response.text
        except Exception as e:
            print(f"Error: {e}")
            return ["missing"]
        return response_text
