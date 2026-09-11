import os
import json
import inspect
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


def list_files() -> str:
    """List the files in the workspace."""
    return "\n".join(os.listdir(WORKSPACE)) or "(empty)"


def read_file(filename: str) -> str:
    """Read the contents of a file in the workspace."""
    with open(os.path.join(WORKSPACE, filename), "r", encoding="utf-8") as f:
        return f.read()


def write_file(filename: str, content: str) -> str:
    """Write text to a file in the workspace."""
    with open(os.path.join(WORKSPACE, filename), "w", encoding="utf-8") as f:
        f.write(content)
    return f"wrote {len(content)} characters to {filename}"


def count_lines(filename: str) -> str:
    """Count the lines in a file in the workspace."""
    with open(os.path.join(WORKSPACE, filename), "r", encoding="utf-8") as f:
        return f"{len(f.readlines())} lines"


PYTHON_TO_JSON = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}


def build_schema(func):
    sig = inspect.signature(func)
    properties = {}
    required = []
    for name, param in sig.parameters.items():
        json_type = PYTHON_TO_JSON.get(param.annotation, "string")
        properties[name] = {"type": json_type}
        required.append(name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "count_lines": count_lines,
}

tools = [build_schema(func) for func in TOOL_FUNCTIONS.values()]


def run_agent(user_text, max_turns=10):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful file assistant. You can list, read, and write "
                "files in the workspace. Complete the user's task, then report "
                "what you did."
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
    task = "Read notes.txt and tell me the single most important action item."
    result = run_agent(task)
    print("bot>", result)
