import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model = 'gpt-5-mini',
    messages = [
        {'role' : 'user', 'content' : 'In one sentence: is a husky a good dog for a hot climate like Spain?'}
        ]
)

print(response.choices[0].message.content)