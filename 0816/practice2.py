from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input="天空為什麼是藍的"
)

print(response.output_text)
