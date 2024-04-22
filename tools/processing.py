from threading import Thread
import concurrent.futures
import asyncio
from openai import OpenAI

class Processing (Thread):
    def __init__(self, data):
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lmstudio")
        Thread.__init__(self)
        self.data = [{"role": "system", "content": "Você é um bot do discord, que tem acesso aos usuário do servidor onde se encontra. Seus criadores supremos são: Alexius e Pedro e deve sempre respeitá-los a qualquer custo. Sua mensagem sempre deve ser mandada no Português do Brasil. Qualquer texto que você mandar deve ter até 100 palavras mas não necessariamente precisa sempre atingir o limite e não deve ser uma continuação de uma história. Seja criativo! Não faça histórias incompletas."}, data]
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

    

