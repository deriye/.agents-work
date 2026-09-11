import os
import json
import subprocess
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

# Only these programs may ever run. Everything else is refused.
ALLOWED_COMMANDS = {"echo", "dir", "type", "findstr"}


def run_command(command):
    parts = command.split()
    if not parts:
        return "ERROR: empty command."
    program = parts[0]
    if program not in ALLOWED_COMMANDS:
        return (
            f"BLOCKED: '{program}' is not allowed. "
            f"Allowed programs: {sorted(ALLOWED_COMMANDS)}"
        )

    result = subprocess.run(
        command,
        shell=True,
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=10,
    )
    output = result.stdout + result.stderr
    return output.strip() or "(no output)"


TOOL_FUNCTIONS = {
    "run_command": run_command,
}


tools = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run a shell command in the workspace. Only these programs are "
                "allowed: echo, dir, type, findstr."
            ),
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
]


def run_agent(user_text, max_turns=10):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a shell assistant. Use run_command to inspect the "
                "workspace. Complete the user's task, then report what you found."
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
    task = "List the files in the workspace and tell me how many there are."
    result = run_agent(task)
    print("bot>", result)
