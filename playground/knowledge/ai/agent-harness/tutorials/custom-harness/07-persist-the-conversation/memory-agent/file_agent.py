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
WORKSPACE = "workspace"
HISTORY_FILE = "history.jsonl"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return None

    messages = []

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                messages.append(json.loads(line))

    return messages or None


def append_history(messages, already_saved):
    """Append only the messages we haven't written yet.

    `already_saved` is how many messages are already on disk. We slice from
    there, write each new message as its own line, and return the new count
    so the caller  can track it for next time.
    """
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for message in messages[already_saved:]:
            f.write(json.dumps(message) + "\n")

    return len(messages)


def _safe_path(filename):
    full = os.path.normpath(os.path.join(WORKSPACE, filename))

    if not full.startswith(os.path.normpath(WORKSPACE)):
        raise ValueError("path escapes the workspace")

    return full


def list_files():
    return "\n".join(os.listdir(WORKSPACE)) or "(empty)"


def read_file(filename):
    with open(_safe_path(filename), "r", encoding="utf-8") as f:
        return f.read()


def write_file(filename, content):
    with open(_safe_path(filename), "w", encoding="utf-8") as f:
        f.write(content)

    return f"wrote {len(content)} characters to {filename}"


TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
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
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text to a file in the workspace",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filename", "content"],
            },
        },
    },
]


def run_turn(messages, max_turns=10):
    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=tools
        )
        message = response.choices[0].message

        if not message.tool_calls:
            messages.append({"role": "assistant", "content": message.content})
            print("bot>", message.content)
            return message.content

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in message.tool_calls
                ],
            }
        )

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"    [turn {turn + 1}] {name}({args})")

            func = TOOL_FUNCTIONS[name]
            result = func(**args)

            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": str(result)}
            )

    return "Stopped: reached the turn limit."


if __name__ == "__main__":
    messages = load_history()

    if messages is None:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a careful file assistant. You can list, read, and"
                    "write files in the workspace. Complete the user's task, "
                    "then report what you did."
                ),
            }
        ]
        print("Started a new conversation.")
    else:
        print(f"Resumed a conversation with {len(messages)} messages.")

    # Everything we just loaded is already on disk - that's our starting
    # high-water mark. A brand-new session starts with 0.
    saved_count = len(messages) if messages else 0
    
    while True:
        user_text = input("you> ")
        if user_text.strip().lower() in {"quit", "exit"}:
            break

        messages.append({"role": "user", "content": user_text})
        run_turn(messages)
        saved_count = append_history(messages, saved_count)
