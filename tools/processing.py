from threading import Thread
import concurrent.futures
import asyncio
from openai import OpenAI

# This class is responsible for processing the AI requests.

class Processing (Thread):
    def __init__(self, data):
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lmstudio")
        Thread.__init__(self)
        self.data = [{"role": "system", "content": "I'm a Discord bot with server access granted by my creators, Alexius and Pedro. Always honoring them above all. Messages are in American english, concise yet impactful. Creativity flows within 100 words, no unfinished stories. Let's engage!"}, data]
        self.future = concurrent.futures.Future()

    def run(self):
        result = []
        for chunk in self.client.chat.completions.create(
            model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
            messages=self.data,
            temperature=0.7,
            max_tokens=1000,
            stream=True,
            ):
            result.append(chunk)
        self.future.set_result(result)

    

