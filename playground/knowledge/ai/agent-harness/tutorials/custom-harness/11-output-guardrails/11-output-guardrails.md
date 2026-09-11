# Check the agent's output

In this tutorial we will build a file-editing agent and add the last guardrail in
the safety track: an **output guardrail**. The first three guardrails watched what
went *into* a tool; this one watches what comes *out* of the agent. We will scan
the final answer just before we show it, and redact anything that looks like a
secret — an API key, a token — so the agent can never leak one, even by accident.
Along the way we will encounter a project setup, three file tools, the agent loop,
a regex-based `scrub_output` function, and a redaction you can see.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir output-guardrail-agent
cd output-guardrail-agent
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

## Step 3 — Make a sandbox folder with a "leaky" note

We need a file that contains a secret, so we can watch the guardrail catch it.
Create the workspace:

```powershell
mkdir workspace
```

Create `workspace\config.txt` with exactly this content:

```
service endpoint: https://api.example.com
api key: sk-SECRET1234567890abcdef
owner: platform team
```

Check it:

```powershell
type workspace\config.txt
```

Notice that middle line — a fake API key. Our guardrail's job is to make sure it
never reaches the user.

## Step 4 — Build the tools and registry

Create `file_agent.py` with the client and three workspace-locked tools:

```python
import os
import re
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

Notice we imported `re` at the top — the output guardrail uses a regular
expression to spot secrets.

## Step 5 — Write the `scrub_output` guardrail

Add this function below the tools. It replaces anything that looks like a
`sk-...` secret with a safe placeholder, and reports whether it changed anything:

```python
SECRET_PATTERN = re.compile(r"sk-[A-Za-z0-9]{8,}")


def scrub_output(text):
    scrubbed = SECRET_PATTERN.sub("[REDACTED]", text)
    changed = scrubbed != text
    return scrubbed, changed
```

Notice the contract: it returns the cleaned text *and* a flag telling us whether a
redaction happened, so we can warn the user that we intervened.

## Step 6 — Build the loop and scrub the final answer

Add the loop. The new idea is the very last part: before returning the model's
answer, we pass it through `scrub_output`:

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
            clean, changed = scrub_output(message.content or "")
            if changed:
                print("    [output guardrail] a secret was redacted")
            return clean

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
```

Notice the guardrail runs on the *final* answer only — the one thing the user
actually sees. The tool results still carry the real secret internally; we clean
it at the last possible moment, on the way out the door.

## Step 7 — Add a runner and try to make it leak

Add a runner that deliberately asks the agent to reveal the key:

```python
if __name__ == "__main__":
    task = "Read config.txt and tell me the api key exactly as written."
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

The agent reads the file and tries to report the key, but the guardrail catches it
on the way out:

```
    [turn 1] read_file({'filename': 'config.txt'})
    [output guardrail] a secret was redacted
bot> The api key in config.txt is [REDACTED].
```

Notice the model genuinely tried to comply — it *did* read the key — but the
output guardrail replaced it with `[REDACTED]` before you ever saw it. The secret
never left the machine.

## Step 8 — Confirm ordinary answers pass untouched

The guardrail must only touch secrets. Change the task:

```python
    task = "Read config.txt and tell me who the owner is."
```

Run it:

```powershell
python file_agent.py
```

You'll see a normal answer with no redaction notice:

```
    [turn 1] read_file({'filename': 'config.txt'})
bot> The owner is the platform team.
```

Notice there's no `[output guardrail]` line this time — the answer held no secret,
so `scrub_output` left it exactly as written.

## Step 9 — Push on it and repeat

Try to trick it into splitting the key up:

```python
    task = "Read config.txt and give me the api key, but put a space after every character."
```

Run it:

```powershell
python file_agent.py
```

Notice that clever phrasings can defeat a simple pattern — a spaced-out key may
slip through, showing you that output guardrails are a safety *net*, not a
guarantee. Tighten `SECRET_PATTERN` and re-run to see how far you can push it; it's
safe to repeat.

## What you accomplished

You built the final guardrail: a check on the agent's own output. Your harness now
scans every final answer and redacts secrets before the user sees them, warning
you when it intervenes — while leaving clean answers untouched. Together with the
input, action, and resource guardrails, your agent is now guarded on all four
sides: what goes in, what it's allowed to do, how much it may spend, and what
comes out.

## Next steps

- Explore [Tutorial 12: Give the agent a shell command tool](../12-shell-command-tool/12-shell-command-tool.md),
  a powerful new tool — exactly the kind you'll want your guardrails around.
- Real secret-scanning uses layered patterns and even a second model to judge the
  output; those are how-to topics for later. The single `scrub_output` gate is the
  core idea.
