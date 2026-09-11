import os
import json
import httpx
import truststore
from dotenv import load_dotenv
from openai import OpenAI

truststore.inject_into_ssl()
load_dotenv()

client = OpenAI(
    base_url=os.environ["LITELLM_BASE_URL"],
    api_key=os.environ["LITELLM_API_KEY"],
)

MODEL = "claude-opus-4-8"
MAX_FETCH_CHARS = 2000


def fetch_url(url):
    if not url.startswith(("http://", "https://")):
        return "ERROR: url must start with http:// or https://"
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
    except Exception as error:
        return f"ERROR: {type(error).__name__}: {error}"

    text = response.text
    if len(text) > MAX_FETCH_CHARS:
        text = text[:MAX_FETCH_CHARS] + f"\n...[truncated, page was {len(response.text)} characters]"
    return f"HTTP {response.status_code}\n{text}"


TOOL_FUNCTIONS = {
    "fetch_url": fetch_url,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Download a web page and return its text (truncated).",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
]


def run_agent(user_text, max_turns=10):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a research assistant. Use fetch_url to read web pages. "
                "Complete the user's task, then report what you found."
            ),
        },
        {"role": "user", "content": user_text},
    ]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=tools
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"    [turn {turn + 1}] {name}({args})")

            func = TOOL_FUNCTIONS[name]
            result = func(**args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                }
            )

    return "Stopped: reached the turn limit."


if __name__ == "__main__":
    task = "Fetch https://example.com and tell me the main heading on the page."
    result = run_agent(task)
    print("bot>", result)
