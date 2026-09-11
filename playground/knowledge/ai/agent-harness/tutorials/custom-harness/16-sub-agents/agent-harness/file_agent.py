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


WORKER_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
}

worker_tools = [
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


def run_worker(task, max_turns=8):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a file worker. Use the tools to inspect the workspace "
                "and answer the task in one or two sentences."
            ),
        },
        {"role": "user", "content": task},
    ]

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=worker_tools
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            func = WORKER_FUNCTIONS[name]
            result = func(**args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                }
            )

    return "Worker stopped: reached the turn limit."


def delegate(task):
    print(f"      -> delegating: {task}")
    answer = run_worker(task)
    print(f"      <- worker done")
    return answer


MAIN_FUNCTIONS = {
    "delegate": delegate,
}

main_tools = [
    {
        "type": "function",
        "function": {
            "name": "delegate",
            "description": (
                "Hand a focused file-inspection task to a worker agent and get "
                "back its answer. Describe the task in one sentence."
            ),
            "parameters": {
                "type": "object",
                "properties": {"task": {"type": "string"}},
                "required": ["task"],
            },
        },
    },
]


def run_agent(user_text, max_turns=10):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a project lead. You cannot read files yourself. Use the "
                "delegate tool to send file tasks to a worker, then summarise the "
                "results for the user."
            ),
        },
        {"role": "user", "content": user_text},
    ]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=main_tools
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"    [turn {turn + 1}] {name}({args})")

            func = MAIN_FUNCTIONS[name]
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
    task = "Find out what ticket is in tasks.txt and what the notes say the next meeting is."
    result = run_agent(task)
    print("bot>", result)
