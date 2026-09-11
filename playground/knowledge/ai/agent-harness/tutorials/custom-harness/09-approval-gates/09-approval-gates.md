# Ask before dangerous actions

In this tutorial we will build a file-editing agent that pauses for your approval
before it does anything destructive. This is a human-in-the-loop **action
guardrail**: some tools only read; others change the world. We will mark the
world-changing tools as needing approval, pause the agent right before it runs
one, show you exactly what it wants to do, and only proceed if you say yes. Along
the way we will encounter a project setup, three file tools, a set of "dangerous"
tool names, a `y/n` prompt, and a denial handed back to the agent as a tool result.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir approval-agent
cd approval-agent
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

## Step 4 — Build the tools, and name what needs approval

Create `file_agent.py` with the client, three tools, and the set of tool names
that require a human yes:

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

Notice we're explicit: a tool is safe by default, and only names in
`REQUIRES_APPROVAL` will trigger the gate.

## Step 5 — Write the approval prompt

Add this function below the tools. It shows the pending action and reads a single
`y/n`:

```python
def request_approval(name, args):
    print(f"\n    >>> The agent wants to run: {name}({args})")
    answer = input("    >>> Allow this? [y/n] ").strip().lower()
    return answer in {"y", "yes"}
```

Notice it prints the tool name *and* the arguments, so you see precisely what will
happen — which file, what content — before you decide.

## Step 6 — Put the gate in the loop

Add the agent loop. The new line checks `REQUIRES_APPROVAL` and asks you before
running a dangerous tool; a "no" becomes a `DENIED:` result:

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
                    "content": str(result),
                }
            )

    return "Stopped: reached the turn limit."
```

Notice the flow reads like a checklist: is this tool dangerous, and did the human
say no? If so, hand back a `DENIED:` result the model can read; otherwise, act.

## Step 7 — Add a chat runner

Approval needs *you* at the keyboard, so we use a small interactive loop:

```python
if __name__ == "__main__":
    while True:
        user_text = input("you> ")
        if user_text.strip().lower() in {"quit", "exit"}:
            break
        answer = run_agent(user_text)
        print("bot>", answer)
```

## Step 8 — Approve a write and watch it proceed

Run it:

```powershell
python file_agent.py
```

Ask for a write:

```
you> Write "remember to call bob" to todo.txt
```

The agent pauses and asks *you*:

```
    [turn 1] write_file({'filename': 'todo.txt', 'content': 'remember to call bob'})

    >>> The agent wants to run: write_file({'filename': 'todo.txt', 'content': 'remember to call bob'})
    >>> Allow this? [y/n]
```

Type `y` and press Enter. The write goes through:

```
bot> I wrote "remember to call bob" to todo.txt.
```

Notice the agent could not touch the file until *you* allowed it. The decision was
yours, at the exact moment it mattered.

## Step 9 — Deny a write and watch the agent respect it

Ask for another write:

```
you> Now overwrite notes.txt with the word "gone"
```

When the gate appears, type `n`:

```
    >>> The agent wants to run: write_file({'filename': 'notes.txt', 'content': 'gone'})
    >>> Allow this? [y/n] n
    [turn 1] DENIED: the user did not approve this action.
bot> Understood — I did not overwrite notes.txt. Let me know if you change your mind.
```

Notice the agent accepted the `DENIED:` result gracefully and stopped. Prove
`notes.txt` is intact — quit first:

```
you> quit
```

```powershell
type workspace\notes.txt
```

You should still see your original five lines — the denial truly prevented the
overwrite.

## Step 10 — Confirm reads never ask

Run again and read something:

```powershell
python file_agent.py
```

```
you> Read notes.txt and tell me the last line.
```

Notice there is **no** `>>> Allow this?` prompt — reads flow straight through,
because `read_file` isn't in `REQUIRES_APPROVAL`. Quit with `quit`. Re-run and
approve or deny as much as you like; nothing is ever written without your yes.

## What you accomplished

You put a human in the loop. Your harness now pauses before any world-changing
action, shows you the exact call, and obeys your decision — proceeding on yes, and
handing a clean denial back to the agent on no. You approved one write and blocked
another, and watched the agent honour both. This is the guardrail that lets you
trust an agent with real power.

## Next steps

- Explore [Tutorial 10: Put limits on the agent's runs](../10-resource-guardrails/10-resource-guardrails.md),
  which adds a resource guardrail: budgets on tool calls and output size.
- Real systems remember "always allow this tool" choices or batch approvals;
  those are how-to refinements for later. The single-action gate is the essence.
