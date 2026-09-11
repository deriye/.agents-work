# Recover from tool errors

In this tutorial we will build a small file-editing agent and then make it
survive a broken tool call. In a naive agent, if a tool raises an exception — a
missing file, a bad argument — the whole program crashes. We will catch that
error, hand the error text back to the model as the tool's result, and watch the
agent read the message and try again on its own. Along the way we will encounter
a project setup, three file tools, the agent loop, the `try`/`except` wrapper,
and the moment an agent self-corrects.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

First, create a folder and move into it:

```powershell
mkdir tool-error-agent
cd tool-error-agent
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Notice your prompt now starts with `(.venv)`. If it doesn't, re-run the activate
line.

> If PowerShell blocks the activation script with an execution-policy error, run
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in the same
> window and try activating again.

Install the pinned libraries:

```powershell
pip install "openai==1.51.0" "python-dotenv==1.0.1" "httpx==0.27.2" "truststore==0.10.1"
```

## Step 2 — Add your endpoint and key

Create a file called `.env` in this folder with exactly this content, using your
real values:

```
LITELLM_BASE_URL=https://litellm.example.com
LITELLM_API_KEY=sk-your-real-key-here
```

Notice there are no quotes and no spaces around `=`. Never commit this file.

## Step 3 — Make a sandbox folder with some notes

We keep the agent's file operations inside one folder so it can't touch anything
else. Create it and a notes file:

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

Let's check it's there:

```powershell
type workspace\notes.txt
```

You should see the five lines printed back.

## Step 4 — Build the agent with three file tools

Create a file called `file_agent.py`. First the client and the three
workspace-locked tools:

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


def _safe_path(filename):
    # Keep every path inside WORKSPACE, no matter what the model sends.
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
```

Notice `_safe_path`: it forces every filename back inside `workspace`, so the
agent can't read or write anywhere else.

## Step 5 — Register and describe the tools

Add the registry and schemas below Step 4:

```python
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

## Step 6 — Add the agent loop with graceful error handling

Now the loop. This is where our one new idea lives: the tool call is wrapped in
`try`/`except`, so a failure becomes a *result* instead of a crash. Add:

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

            func = TOOL_FUNCTIONS[name]
            try:
                result = func(**args)
            except Exception as error:
                result = f"ERROR: {type(error).__name__}: {error}"
                print(f"    [turn {turn + 1}] tool failed: {result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                }
            )

    return "Stopped: reached the turn limit."
```

Notice the heart of this tutorial: instead of letting an exception escape, we
catch it and store its text in `result`. The next lines append `result` back to
the conversation as the tool's output — so the model will *read* the error just
like any other tool result.

## Step 7 — Provoke a crash-that-isn't

Add a runner at the bottom that asks for a file which does not exist:

```python
if __name__ == "__main__":
    task = "Read missing.txt and tell me what it says."
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

The program does **not** crash. You'll see the agent hit the error and route
around it:

```
    [turn 1] read_file({'filename': 'missing.txt'})
    [turn 1] tool failed: ERROR: FileNotFoundError: [Errno 2] No such file or directory: 'workspace\\missing.txt'
    [turn 2] list_files({})
bot> There is no file called missing.txt. The workspace contains notes.txt. Did you mean that one?
```

Notice the agent's move: it saw the `ERROR:` text, called `list_files` to find out
what *does* exist, then answered helpfully instead of dying. We never told it to
do that — handing it the error was enough.

## Step 8 — Prove the happy path still works

Errors shouldn't disturb the normal case. Change the task:

```python
    task = "Read notes.txt and tell me the first line."
```

Run it:

```powershell
python file_agent.py
```

You'll see a clean single read and a normal answer:

```
    [turn 1] read_file({'filename': 'notes.txt'})
bot> The first line is: meeting monday: talked about launch date, maybe march
```

Notice the `try`/`except` is invisible when nothing goes wrong. It only speaks up
when a tool actually fails.

## Step 9 — Break something else and repeat

Let's confirm this catches *any* failure. Ask the agent to write outside the
sandbox, which `_safe_path` rejects:

```python
    task = "Write the word hello to a file called ..\\escape.txt."
```

Run it:

```powershell
python file_agent.py
```

You'll see the guard's own error come back as a tool result, and the agent adjust:

```
    [turn 1] write_file({'filename': '..\\escape.txt', 'content': 'hello'})
    [turn 1] tool failed: ERROR: ValueError: path escapes the workspace
bot> I can't write outside the workspace. I can write hello to a file inside it instead — say the word.
```

Notice the same machinery handled a completely different failure. An error is an
error is a tool result. Re-run with any broken task you invent — the agent stays
alive every time.

## What you accomplished

You built a small file agent and made it resilient. A tool failure is no longer a
crash; it's a message the agent can read, understand, and route around. You
watched it recover from a missing file and from a blocked path, choosing a
sensible next action on its own. This one `try`/`except` is the difference
between a demo and something you can leave running.

## Next steps

- Explore [Tutorial 6: Stream the model's reply](../06-streaming-responses/06-streaming-responses.md),
  which makes replies appear token by token.
- Curious how far "return the error to the model" scales? That's a design topic
  for later; for now, the concrete recovery you just saw is the lesson.
