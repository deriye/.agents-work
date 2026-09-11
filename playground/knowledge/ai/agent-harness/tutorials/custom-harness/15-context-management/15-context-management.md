# Keep the conversation from growing forever

In this tutorial we will stop a long-running agent from overflowing the model's
context. Every turn appends more messages, and eventually the conversation gets
too big to send. The fix is a `trim_history` step that always keeps the system
message but drops the oldest turns once the list gets long. We will set up the
project, build a file agent, add the trim step to the loop, and watch the message
count hold steady across many turns instead of climbing without limit. Along the
way we will encounter a growing message list, a window size, and a trim that
protects the system prompt.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir context-agent
cd context-agent
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

## Step 3 — Make a sandbox folder with a few files

```powershell
mkdir workspace
```

Create a handful of small files so the agent has several turns of work to do:

```powershell
"apples" | Out-File -Encoding utf8 workspace\a.txt
"bananas" | Out-File -Encoding utf8 workspace\b.txt
"cherries" | Out-File -Encoding utf8 workspace\c.txt
"dates" | Out-File -Encoding utf8 workspace\d.txt
```

## Step 4 — Build the file agent

Create `file_agent.py` with the usual tools and registry:

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


def list_files():
    return "\n".join(os.listdir(WORKSPACE)) or "(empty)"


def read_file(filename):
    with open(os.path.join(WORKSPACE, filename), "r", encoding="utf-8") as f:
        return f.read()


TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
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
]
```

## Step 5 — Write the trim step

This is the heart of the tutorial. `trim_history` keeps the first message (the
system prompt) always, and keeps only the most recent `MAX_HISTORY` messages after
it:

```python
MAX_HISTORY = 8


def role_of(message):
    # Messages are plain dicts, except the assistant reply, which is an SDK
    # object. This reads the role from either one.
    if isinstance(message, dict):
        return message.get("role")
    return getattr(message, "role", None)


def trim_history(messages):
    if len(messages) <= MAX_HISTORY + 1:
        return messages
    system = messages[0]
    recent = messages[-MAX_HISTORY:]
    # A "tool" message must follow the assistant message that requested it.
    # If the cut landed just after that assistant message, drop the now-orphaned
    # tool replies so the request we send is always valid.
    while recent and role_of(recent[0]) == "tool":
        recent = recent[1:]
    return [system] + recent
```

Notice the system message is pulled out and pinned first, so no matter how much we
drop, the agent never forgets who it is. Only the middle — the oldest turns — gets
discarded.

Notice the `while` guard, too: a `tool` message only makes sense right after the
`assistant` message that asked for it, so if the window boundary would leave a
`tool` reply stranded at the top, we drop it. Without this, lowering `MAX_HISTORY`
or changing the task could cut between an `assistant` tool call and its `tool`
reply, and the API would reject the request.

## Step 6 — Add the loop and call trim every turn

Add the loop. The one new line is `messages = trim_history(messages)` at the top of
each turn, plus a print so we can watch the count:

```python
def run_agent(user_text, max_turns=20):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful file assistant. Read files one at a time when "
                "asked. Complete the user's task, then report what you found."
            ),
        },
        {"role": "user", "content": user_text},
    ]

    for turn in range(max_turns):
        messages = trim_history(messages)
        print(f"    [turn {turn + 1}] history size: {len(messages)}")

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

Notice `trim_history` runs *before* each API call, so the request we send never
grows past the window even though the local `messages` list keeps being appended
to within a turn.

## Step 7 — Give it a multi-turn task and watch the size hold

Add a runner with a task that forces several read turns:

```python
if __name__ == "__main__":
    task = (
        "Read a.txt, then b.txt, then c.txt, then d.txt, one at a time. "
        "Then tell me all four contents in one sentence."
    )
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

The history size climbs, then flattens at the window instead of growing forever:

```
    [turn 1] history size: 2
    [turn 2] history size: 4
    [turn 3] history size: 6
    [turn 4] history size: 8
    [turn 5] history size: 9
    [turn 6] history size: 9
bot> The files contain: apples, bananas, cherries, and dates.
```

Notice the size holds at its ceiling of 9 — the pinned system message plus the last
8 — no matter how many more turns run. (On a turn where the window boundary would
strand a `tool` reply, the guard drops it and you'll see one fewer for that turn.)
The conversation can now go on indefinitely without the request ballooning.

## Step 8 — Shrink the window and repeat

Make the window tiny to prove the trim is doing the work:

```python
MAX_HISTORY = 4
```

Run it again:

```powershell
python file_agent.py
```

```
    [turn 1] history size: 2
    [turn 2] history size: 4
    [turn 3] history size: 5
    [turn 4] history size: 5
    [turn 5] history size: 5
bot> The files contain: apples, bananas, cherries, and dates.
```

Notice the ceiling dropped to 5 (system + 4). The agent still finishes because the
recent turns hold the information it needs right now, and the orphaned-`tool` guard
keeps every trimmed request valid even at this tiny window. Raise or lower
`MAX_HISTORY` and re-run; it's safe to repeat.

## What you accomplished

You gave your agent a memory that can't overflow. `trim_history` pins the system
prompt and keeps a fixed window of recent messages, dropping the oldest turns so
the request sent to the model stays a steady size no matter how long the run goes.
You watched the history climb and then hold flat at the window, and you shrank the
window to prove the trim was in control.

## Next steps

- Explore [Tutorial 16: Delegate work to a sub-agent](../16-sub-agents/16-sub-agents.md),
  which splits a big job across more than one agent.
- Summarising the dropped turns into a running note, instead of discarding them, is
  a richer strategy for later. A fixed window is the concrete, no-dependencies start.
