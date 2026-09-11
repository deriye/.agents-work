import os
import truststore
from dotenv import load_dotenv
from openai import OpenAI

truststore.inject_into_ssl()
load_dotenv()

client = OpenAI(
    base_url=os.environ["LITELLM_BASE_URL"], api_key=os.environ["LITELLM_API_KEY"]
)

response = client.chat.completions.create(
    model="claude-opus-4-8",
    messages=[{"role": "user", "content": "Say hello in exactly five words."}],
)

print(response.choices[0].message.content)
