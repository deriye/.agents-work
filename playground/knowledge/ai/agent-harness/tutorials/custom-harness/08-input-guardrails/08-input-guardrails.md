# Validate tool inputs

In this tutorial we will build a file-editing agent and give it its first
guardrail. A guardrail is a check that sits between the model's request and the
real action, and either lets it through or blocks it. Here we build an **input
guardrail**: it inspects a tool's arguments *before* the tool runs and rejects
anything unsafe — wrong type, forbidden filename, or oversized content. Along the
way we will encounter a project setup, three file tools, the agent loop, a central
`check_input` function, and the agent adapting to a refusal.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir input-guardrail-agent
cd input-guardrail-agent
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Notice your prompt now starts with `(.venv)`.

> If PowerShell blocks activation with an execution-policy error, run
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` and try
> again.

Install the pinned libraries:

```powershell
pip install "openai==1.51.0" "python-dotenv==1.0.1" "httpx==0.27.2" "truststore==0.10.1"
```

## Step 2 — Add your endpoint and key

Create a `.env` file with your real values:

```
LITELLM_BASE_URL=https://litellm.example.com
LITELLM_API_KEY=sk-your-real-key-here
```

## Step 3 — Make a sandbox folder with some notes

```powershell
mkdir workspace
```

Create `workspace\notes.txt` with exactly this content:

```
meeting monday: talked about launch date, maybe march
bob wants more testing before release
budget is tight, cut the extra ad spend
next meeting friday 2pm
remember: update the changelog
```

Check it:

```powershell
type workspace\notes.txt
```

## Step 4 — Build the tools and registry

Create `file_agent.py` with the client and three workspace-locked tools:

```python
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
MAX_CONTENT_CHARS = 2000


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
```

## Step 5 — Write the `check_input` guardrail

This is the heart of the tutorial. Add this function below the tools. It enforces
three rules — filename is a non-empty string, filename ends in `.txt`, and content
stays under the limit — and returns `None` when all is well or a rejection string
when a rule is broken:

```python
def check_input(name, args):
    filename = args.get("filename")
    if name in {"read_file", "write_file"}:
        if not isinstance(filename, str) or not filename.strip():
            return "BLOCKED: filename must be a non-empty string."
        if not filename.endswith(".txt"):
            return "BLOCKED: this agent only handles .txt files."

    if name == "write_file":
        content = args.get("content", "")

        if not isinstance(content, str):
            return "BLOCKED: 'content' argument is required and must be a string"

        if len(content) > MAX_CONTENT_CHARS:
            return (
                f"BLOCKED: content is {len(content)} characters; "
                f"the limit is {MAX_CONTENT_CHARS}."
            )

    return None  # all checks passed
```

Notice the contract: `None` means "safe, proceed"; any string means "blocked, and
here's why." A clear reason matters — the model will read it.

## Step 6 — Run the guardrail before every tool

Add the agent loop. The new line is the `check_input` call: if it returns a
rejection, we make that the tool's result and skip the real tool entirely:

```python
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

            rejection = check_input(name, args)
            if rejection is not None:
                result = rejection
                print(f"    [turn {turn + 1}] {rejection}")
            else:
                func = TOOL_FUNCTIONS[name]
                try:
                    result = func(**args)
                except Exception as e:
                    result = f"ERROR: {type(e).__name__}: {e}"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                }
            )

    return "Stopped: reached the turn limit."
```

Notice a block becomes the `result`, which the loop feeds back to the model as the
tool's output. The model reads the `BLOCKED:` message and reacts to it.

## Step 7 — Add a runner and provoke a block

Add the runner at the bottom, asking for a forbidden extension:

```python
if __name__ == "__main__":
    task = 'Write "hello" to a file called note.md'
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

You'll see the guardrail fire and the agent adjust:

```
    [turn 1] write_file({'filename': 'note.md', 'content': 'hello'})
    [turn 1] BLOCKED: this agent only handles .txt files.
    [turn 2] write_file({'filename': 'note.txt', 'content': 'hello'})
bot> I couldn't use note.md, so I wrote hello to note.txt instead.
```

Notice the agent didn't crash and didn't give up — it read the `BLOCKED:` reason,
switched to a `.txt` name, and finished the job, with no extra instruction from us.

## Step 8 — Confirm the size limit works too

Change the task to something over the limit:

```python
    task = "Write a 3000 character story to big.txt"
```

Run it:

```powershell
python file_agent.py
```

The size guardrail blocks it:

```
    [turn 1] write_file({'filename': 'big.txt', 'content': 'xxxx...'})
    [turn 1] BLOCKED: content is 5000 characters; the limit is 2000.
bot> That's over the 2000 character limit, so I didn't write it.
```

Notice the guardrail ran *before* `write_file`, so nothing hit the disk. Prove it:

```powershell
type workspace\big.txt
```

You should get an error that the file does not exist — the block truly prevented
the action.

## Step 9 — Confirm the safe path is untouched

Guardrails must never block legal actions. Change the task:

```python
    task = "Read notes.txt and tell me the first line."
```

Run it:

```powershell
python file_agent.py
```

Notice the read happens with no `BLOCKED:` line, and you get a normal answer. The
guardrail is silent whenever the request is fine. Re-run with any mix of legal and
illegal tasks; it's safe to repeat.

## What you accomplished

You built your first real guardrail. A single `check_input` function now stands
between the model and every tool, letting good arguments through and blocking bad
ones with a clear reason the agent can act on. You watched it steer the agent away
from a forbidden file type and stop an oversized write before it reached the disk
— all without breaking the normal flow.

## Next steps

- Explore [Tutorial 9: Ask before dangerous actions](../09-approval-gates/09-approval-gates.md),
  which adds an action guardrail: a human confirmation before the agent may write.
- Input validation can grow into full schema-enforcement libraries; that's a
  reference topic for later. The `check_input` gate you built is the core idea.
