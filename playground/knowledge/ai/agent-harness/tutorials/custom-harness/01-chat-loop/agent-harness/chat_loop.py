import os
import truststore
from dotenv import load_dotenv
from openai import OpenAI

truststore.inject_into_ssl()
load_dotenv()

client = OpenAI(
    base_url=os.environ["LITELLM_BASE_URL"],
    api_key=os.environ["LITELLM_API_KEY"]
)

MODEL = "claude-opus-4-8"

messages = [
    {"role": "system", "content": "You are a concise, friendly assistant."}
]

while True:
    user_text = input("you> ")

    if user_text.strip() in {"exit", "quit"}:
        print("Goodbye!")
        break

    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )

    reply = response.choices[0].message.content

    messages.append({"role": "assistant", "content": reply})
    print("bot>", reply)