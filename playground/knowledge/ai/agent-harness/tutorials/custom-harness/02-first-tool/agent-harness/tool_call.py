import os
import json
import truststore
from dotenv import load_dotenv
from openai import OpenAI


truststore.inject_into_ssl()
load_dotenv()


client = OpenAI(
    base_url=os.environ["LITELLM_BASE_URL"], api_key=os.environ["LITELLM_API_KEY"]
)


MODEL = "claude-opus-4-8"


def calculator(a, b, op):
    if op == "add":
        return a + b

    if op == "subtract":
        return a - b

    if op == "multiply":
        return a * b

    if op == "divide":
        return a / b

    return "unknown operation"


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Do arithmetic on two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "op": {
                        "type": "number",
                        "enum": ["add", "substract", "multiply", "divide"],
                    },
                },
                "required": ["a", "b", "op"]
            },
        },
    }
]


messages = [
    {"role": "user", "content": "What is 347 multiplied by 29?"}
]

response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools
)

message = response.choices[0].message
print("tool_calls:", message.tool_calls)


tool_call = message.tool_calls[0]
args = json.loads(tool_call.function.arguments)

result = calculator(args["a"], args["b"], args["op"])
print("we computed:", result)

# Record the model's request, then our answer to it.
messages.append(message)
messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(result) 
    }
)

# Ask the model to continue now that it has the result.
followup = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools
)
print("bot>", followup.choices[0].message.content)