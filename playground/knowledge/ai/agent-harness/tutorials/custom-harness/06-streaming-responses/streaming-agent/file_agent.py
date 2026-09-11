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
            "description": "Write text to a file in the workspace.",
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


def stream_turn(messages):
    stream = client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools, stream=True
    )

    full_text = ""
    # tool-call fragments arrive piece by piece, keyed by their index
    tool_calls = {}
    printed_predix = False

    for chunk in stream:
        delta = chunk.choices[0].delta

        # 1) text answer - print each piece the instant it lands
        if delta.content:
            if not printed_predix:
                print("bot> ", end="", flush=True)
                printed_predix = True

            print(delta.content, end="", flush=True)
            full_text += delta.content

        if delta.tool_calls:
            for tc in delta.tool_calls:
                slot = tool_calls.setdefault(
                    tc.index, {"id": None, "name": "", "arguments": ""}
                )

                if tc.id:
                    slot["id"] = tc.id

                if tc.function and tc.function.name:
                    slot["name"] += tc.function.name

                if tc.function and tc.function.arguments:
                    slot["arguments"] += tc.function.arguments

    if full_text:
        print()  # end the line once the text stream is done

    ordered_calls = [tool_calls[i] for i in sorted(tool_calls)]
    return full_text, ordered_calls


def run_agent(user_text, max_turns=10):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful file assistant. You can list, read, and "
                "write files in the workspace. Complete the user's task, then "
                "report what you did."
            ),
        },
        {"role": "user", "content": user_text},
    ]

    for turn in range(max_turns):
        text, tool_calls = stream_turn(messages)

        if not tool_calls:
            # Only text this turn - the answer already streamed above
            return text

        # Record the assistant turn (text, if any, plust the tool calls).
        messages.append(
            {
                "role": "assistant",
                "content": text or None,
                "tool_calls": [
                    {
                        "id": call["id"],
                        "type": "function",
                        "function": {
                            "name": call["name"],
                            "arguments": call["arguments"],
                        },
                    }
                    for call in tool_calls
                ],
            }
        )

        for call in tool_calls:
            name = call["name"]
            args = json.loads(call["arguments"])
            print(f"    [turn {turn + 1}] {name}({args})")

            func = TOOL_FUNCTIONS[name]
            result = func(**args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": str(result)
                }
            )
    
    return "Stopped: reached the turn limit."


if __name__ == "__main__":
    task = "Tell me a story"
    run_agent(task)
