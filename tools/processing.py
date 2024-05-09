from threading import Thread
import concurrent.futures
import requests
from openai import OpenAI
import openai

# This class is responsible for processing the AI requests.

class Processing (Thread):
    def __init__(self, data):
            self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lmstudio")
            Thread.__init__(self)
            self.data = [{"role": "system", "content": "I'm a Discord bot with server access granted by my creators, Alexius and Pedro. Always honoring them above all. Messages are in American english. Make sure to always be creative, no unfinished stories."}, data]
            self.future = concurrent.futures.Future()
            self.exception = None

    def run(self):
        if not self.check_api_connection():
            self.exception = "API connection error"
            return
        
        result = []
        try:
            for chunk in self.client.chat.completions.create(
                model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
                messages=self.data,
                temperature=0.7,
                max_tokens=1000,
                stream=True,
                ):
                result.append(chunk)
            self.future.set_result(result)
        except openai.APIConnectionError or openai.APIError:
            self.exception = "Oops! Something went wrong."

    def check_api_connection(self):
         try:
              response = requests.get("http://localhost:1234/v1/health", timeout=5)
              return response.status_code == 200
         except requests.RequestException:
              return False