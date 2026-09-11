import os
import json
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

def calculator(a, b, op):
    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "cannot divide by zero"
    }

    return ops.get(op, "unknown operation")

def word_count(text):
    return len(text.split())

TOOL_FUNCTIONS = {
    "calculator": calculator,
    "word_count": word_count
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Do arithemtic on two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "op": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                },
                "required": ["a", "b", "op"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "word_count",
            "description": "Count the number of words in a piece of text.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]
            }
        }
    }
]


def run_agent(user_text):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Use tools when they help."
        },
        {
            "role": "user",
            "content": user_text
        }
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )
        message = response.choices[0].message
        messages.append(message)

        # No tool calls means the model gave its final answer.
        if not message.tool_calls:
            return message.content
        
        # Otherwise, run every tool the model asked for.
        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"    [running tool: {name}({args})]")

            func = TOOL_FUNCTIONS[name]
            result = func(**args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result)
                }
            )


if __name__ == "__main__":
    # question = "How many words are in the sentence 'the quick brown fox jumps', and what is that count multiplied by 10?"
    question = "What is 12 times 12?"
    answer = run_agent(question)
    print("bot>", answer)