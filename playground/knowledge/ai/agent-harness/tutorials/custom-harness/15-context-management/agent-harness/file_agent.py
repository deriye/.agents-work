import os
import json
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
WORKSPACE = "workspace"


def list_files():
    return "\n".join(os.listdir(WORKSPACE)) or "(empty)"


def read_file(filename):
    with open(os.path.join(WORKSPACE, filename), "r", encoding="utf-8") as f:
        return f.read()


TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List the files in the workspace.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"],
            },
        },
    },
]


MAX_HISTORY = 8


def trim_history(messages):
    if len(messages) <= MAX_HISTORY + 1:
        return messages
    system = messages[0]
    recent = messages[-MAX_HISTORY:]
    return [system] + recent


def run_agent(user_text, max_turns=20):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful file assistant. Read files one at a time when "
                "asked. Complete the user's task, then report what you found."
            ),
        },
        {"role": "user", "content": user_text},
    ]

    for turn in range(max_turns):
        messages = trim_history(messages)
        print(f"    [turn {turn + 1}] history size: {len(messages)}")

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
    task = (
        "Read a.txt, then b.txt, then c.txt, then d.txt, one at a time. "
        "Then tell me all four contents in one sentence."
    )
    result = run_agent(task)
    print("bot>", result)
