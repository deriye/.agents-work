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
WORKSPACE = "workspace"
REQUIRES_APPROVAL = {"write_file"}


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
    "write_file": write_file
}


tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List the files in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write a text to a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename", "content"]
            }
        }
    }
]


def request_approval(name, args):
    print(f"n   >>> The agent wants to run: {name}({args})")
    answer = input("    >>> Allow this? [y/n]").strip().lower()

    return answer in {"y", "yes"}


def run_agent(user_text, max_turns=10):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful file assistant. You can list, read, and "
                "write files in the workspace. Complete the user's task, then "
                "report what you did."
            )
        },
        {"role": "user", "content": user_text}
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

            if name in REQUIRES_APPROVAL and not request_approval(name, args):
                result = "DENIED: the user did not approve this action."
                print(f"    [turn {turn + 1}] {result}")
            else:
                func = TOOL_FUNCTIONS[name]
                result = func(**args)
            
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result)
                }
            )
    
    return "Stopped: reached the turn limit."



if __name__ == "__main__":
    while True:
        user_text = input("you> ")
        if user_text.strip().lower() in {"quit", "exit"}:
            break
        
        answer = run_agent(user_text)
        print(f"bot> {answer}")