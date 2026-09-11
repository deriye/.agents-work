# Put limits on the agent's runs

In this tutorial we will build a file-editing agent with a **resource guardrail**.
An autonomous agent can burn through calls and produce enormous tool outputs
without meaning to. We will give it a budget on the total number of tool calls per
task and truncate any tool result that comes back too large. Along the way we will
encounter a project setup, three file tools, the agent loop, a running call
counter, a truncation helper, and a clean "budget reached" stop.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir resource-guardrail-agent
cd resource-guardrail-agent
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

Now make one large file so we can see truncation in action later:

```powershell
python -c "open('workspace/big.txt','w').write('word '*300)"
```

## Step 4 — Build the tools, and set the budgets

Create `file_agent.py` with the client, three tools, and two limits:

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
MAX_TOOL_CALLS = 6
MAX_TOOL_OUTPUT_CHARS = 500


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

Notice these limits are separate from the turn limit we'll set in the loop. A
single turn can ask for several tools at once, so counting *tool calls* is a
tighter leash than counting turns.

## Step 5 — Add a truncation helper

Add this function below the tools. It clips any oversized tool result and tells
the model exactly how much it cut:

```python
def truncate(text):
    text = str(text)
    if len(text) <= MAX_TOOL_OUTPUT_CHARS:
        return text
    keep = MAX_TOOL_OUTPUT_CHARS
    return text[:keep] + f"\n...[truncated {len(text) - keep} characters]"
```

Notice it always returns a string and reports the clip, so the model knows the
result was shortened and can reason honestly about it.

## Step 6 — Build the loop that counts calls and truncates output

Add the loop. The two new ideas are the `tool_calls_used` counter that hard-stops
the task, and wrapping every result in `truncate`:

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

    tool_calls_used = 0
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

            tool_calls_used += 1
            if tool_calls_used > MAX_TOOL_CALLS:
                print(f"    [turn {turn + 1}] tool-call budget reached")
                return f"Stopped: exceeded the {MAX_TOOL_CALLS}-tool-call budget."

            func = TOOL_FUNCTIONS[name]
            result = func(**args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": truncate(result),
                }
            )

    return "Stopped: reached the turn limit."
```

Notice we return immediately when the budget is blown — a hard stop, not a polite
request. And every tool result now passes through `truncate`, so no single output
can flood the context.

## Step 7 — Add a runner and trip the output limit

Add the runner, asking the agent to read the big file:

```python
if __name__ == "__main__":
    task = "Read big.txt and tell me roughly how long it is."
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

You'll see the read happen, and the agent works from a clipped result:

```
    [turn 1] read_file({'filename': 'big.txt'})
bot> big.txt was truncated at 500 characters (it noted more was cut), so it's over 500 characters long — a repeated "word ".
```

Notice the model was *told* the content was truncated, so it reasoned about the
clip instead of pretending it saw everything.

## Step 8 — Trip the tool-call budget

Change the task to force many calls:

```python
    task = (
        "List the files, then read notes.txt, big.txt, notes.txt, big.txt, "
        "and notes.txt again, one at a time."
    )
```

Run it:

```powershell
python file_agent.py
```

You'll watch the calls tick up and then hit the wall:

```
    [turn 1] list_files({})
    [turn 2] read_file({'filename': 'notes.txt'})
    [turn 3] read_file({'filename': 'big.txt'})
    ...
    [turn 6] read_file({'filename': 'big.txt'})
    [turn 7] tool-call budget reached
bot> Stopped: exceeded the 6-tool-call budget.
```

Notice the agent was cut off cleanly at the seventh call, no matter what the task
asked for. The budget, not the model, decided when enough was enough.

## Step 9 — Confirm small tasks are unaffected

Change the task to something small:

```python
    task = "Read notes.txt and tell me the first line."
```

Run it:

```powershell
python file_agent.py
```

Notice this uses one tool call and a short result — well under both budgets — so
it finishes normally, no truncation and no stop. Tune `MAX_TOOL_CALLS` and
`MAX_TOOL_OUTPUT_CHARS` and re-run to feel where the limits bite; it's safe to
repeat.

## What you accomplished

You gave your harness a spending limit. It counts every tool call and halts a task
that runs away, and it trims any oversized tool result so a single big file can't
swamp the model — while telling the model honestly that it did so. Your agent can
no longer spiral into an expensive or endless run.

## Next steps

- Explore [Tutorial 11: Check the agent's output](../11-output-guardrails/11-output-guardrails.md),
  the last guardrail in the track, where we inspect the final answer before we
  trust it.
- Counting real tokens and enforcing a money budget needs the API's usage numbers;
  that's a how-to for later. Character budgets are a solid, concrete start.
