# Remember conversations across runs

In this tutorial we will build an interactive file-editing agent whose memory
outlives a single run. We will set up the project, give the agent three file
tools and a chat loop, then persist the message history to a JSON Lines file —
appending only the new messages after every exchange and loading them back on
startup — so you can quit, reopen, and pick up exactly where you left off. Along
the way we will encounter JSON serialization of messages, the reason we store
assistant messages as plain dictionaries, the JSON Lines (`.jsonl`) format, and
why appending beats rewriting the whole file each turn.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir memory-agent
cd memory-agent
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

Create a `.env` file in this folder with your real values:

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

## Step 4 — Build the tools, the registry, and the load/append pair

Create `file_agent.py`. Start with the client, the workspace tools, and — the new
idea — two small functions that read the history file and append to it. We store
history as **JSON Lines** (`.jsonl`): one JSON object per line. That format is
what lets us *append* new messages instead of rewriting the whole file every
turn.

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
HISTORY_FILE = "history.jsonl"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return None
    messages = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                messages.append(json.loads(line))
    return messages or None


def append_history(messages, already_saved):
    """Append only the messages we haven't written yet.

    `already_saved` is how many messages are already on disk. We slice from
    there, write each new message as its own line, and return the new count
    so the caller can track it for next time.
    """
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for message in messages[already_saved:]:
            f.write(json.dumps(message) + "\n")
    return len(messages)


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

Notice `load_history` returns `None` when there's no file yet — that's how we'll
tell a brand-new session from a resumed one. And notice `append_history` never
rewrites existing lines: it only writes the messages past `already_saved`. That
"high-water mark" is the whole trick behind the append strategy — without it we'd
either re-append the entire growing list every turn (duplicating everything) or
fall back to rewriting the file from scratch.

> **Why append, not rewrite?** A single JSON array (`[...]`) can't be appended to
> cleanly — the closing `]` is always in the way, so adding one message means
> rewriting the entire file. JSON Lines sidesteps that: each message is an
> independent line, so `open(..., "a")` just adds to the end. The one rule to
> respect is that we only append messages once they're *finalized* for the turn —
> which is exactly what our loop does below.

## Step 5 — Write a turn that keeps history JSON-friendly

Add the turn function below. The key move: instead of appending the raw SDK
message object (which can't be saved to JSON), we rebuild the assistant message as
a plain dictionary, tool calls and all:

```python
def run_turn(messages, max_turns=10):
    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=tools
        )
        message = response.choices[0].message

        if not message.tool_calls:
            messages.append({"role": "assistant", "content": message.content})
            print("bot>", message.content)
            return message.content

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in message.tool_calls
                ],
            }
        )

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

Notice every item we append to `messages` is now an ordinary dict. Ordinary dicts
save to JSON cleanly, and we copied the `tool_calls` across so the model still
sees, next turn, which tools it asked for.

## Step 6 — Add a resumable chat loop

Add the bottom of the file. It loads history on start, tracks how many messages
are already on disk, and appends the new ones after every turn:

```python
if __name__ == "__main__":
    messages = load_history()
    if messages is None:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a careful file assistant. You can list, read, and "
                    "write files in the workspace. Complete the user's task, "
                    "then report what you did."
                ),
            }
        ]
        print("Started a new conversation.")
    else:
        print(f"Resumed a conversation with {len(messages)} messages.")

    # Everything we just loaded is already on disk — that's our starting
    # high-water mark. A brand-new session starts at 0.
    saved_count = len(messages) if messages else 0

    while True:
        user_text = input("you> ")
        if user_text.strip().lower() in {"quit", "exit"}:
            break

        messages.append({"role": "user", "content": user_text})
        run_turn(messages)
        saved_count = append_history(messages, saved_count)
```

Notice we append immediately after each turn, so `history.jsonl` is always
current — and because `run_turn` has fully finished, every message we append is
finalized (user message, assistant reply, and any tool calls and results). We
carry `saved_count` forward so the next append writes only what's new.

## Step 7 — Start a fresh conversation

Run the program:

```powershell
python file_agent.py
```

Notice it prints `Started a new conversation.` and waits at `you>`. Give it a task
that makes it remember something:

```
you> Read notes.txt and remember the launch month for me.
```

It reads the file and names the month (March). Now quit:

```
you> quit
```

Let's check the memory landed on disk:

```powershell
type history.jsonl
```

You should see one message per line — system, your question, the assistant's
reply, tool calls and results — each a self-contained JSON object. That file *is*
the agent's memory.

## Step 8 — Reopen and prove it remembered

Run the program again:

```powershell
python file_agent.py
```

Notice it now prints `Resumed a conversation with N messages.` Ask something that
only makes sense if it recalls the earlier turn:

```
you> What was that launch month again? Don't read the file, just tell me.
```

It answers `March` from memory — the history we loaded carried the earlier
exchange straight back into the model's context. Quit again with `quit`.

Notice you never re-read the file. The knowledge survived a full restart.

## Step 9 — Repeat, and reset when you want

Run it a few more times, adding a message each session:

```powershell
python file_agent.py
```

Notice `history.jsonl` gains new lines with every exchange, and each run resumes
with a larger message count. When you want a clean slate, delete the file:

```powershell
del history.jsonl
```

The next run starts fresh. It's completely safe to repeat.

## What you accomplished

You gave your agent a persistent memory. By keeping the history as plain
dictionaries, appending them to a JSON Lines file after each turn, and loading
them back on startup, you turned a one-shot script into a session you can leave
and return to. You saw the conversation survive a restart and answer from memory
alone — and you did it by appending only what's new instead of rewriting the
whole file every time.

## Next steps

- Explore [Tutorial 8: Validate tool inputs](../08-input-guardrails/08-input-guardrails.md),
  which begins a guardrails track by checking a tool's arguments before running
  it.
- Notice `history.jsonl` grows without limit. Trimming it before it overflows the
  model's context is its own topic — see
  [Tutorial 15](../15-context-management/15-context-management.md). (Trimming is
  also where an append-only log gets interesting: once you *remove* messages you
  can no longer just append, so you rewrite the file from the trimmed list.)
