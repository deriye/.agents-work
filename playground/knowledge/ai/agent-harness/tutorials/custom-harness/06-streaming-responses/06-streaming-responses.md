# Stream the model's reply

In this tutorial we will build a file-editing agent whose answer appears a piece
at a time, the way text arrives in a chat app, instead of landing all at once
after a long pause. We will set up the project, give the agent three file tools
and an agent loop, then turn streaming on so the answer types itself out live.
Along the way we will encounter the `stream=True` flag, the delta-shaped chunk,
and how to read tool calls out of the same stream so that *every* turn — even a
plain "Tell me a story" with no tools — streams live.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir streaming-agent
cd streaming-agent
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

## Step 5 — Add a helper that streams one model turn

This is the new idea. Add this function below the tools. It asks the model with
`stream=True` and prints each chunk the instant it arrives. Because we stream
*every* turn, the same call also has to collect any tool calls the model makes —
those arrive as deltas too, spread across many chunks, so we stitch them back
together:

```python
def stream_turn(messages):
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        stream=True,
    )

    full_text = ""
    # tool-call fragments arrive piece by piece, keyed by their index
    tool_calls = {}
    printed_prefix = False

    for chunk in stream:
        delta = chunk.choices[0].delta

        # 1) text answer — print each piece the instant it lands
        if delta.content:
            if not printed_prefix:
                print("bot> ", end="", flush=True)
                printed_prefix = True
            print(delta.content, end="", flush=True)
            full_text += delta.content

        # 2) tool call — accumulate the name + argument fragments
        if delta.tool_calls:
            for tc in delta.tool_calls:
                slot = tool_calls.setdefault(
                    tc.index,
                    {"id": None, "name": "", "arguments": ""},
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
```

Notice the ideas at work. `stream=True` changes what the call returns: instead of
one finished message, we get an iterator of small `chunk` objects. Each chunk
carries a `delta` — the *new* fragment since the last chunk. Text arrives at
`delta.content`, which we print immediately with `flush=True`. Tool calls arrive
at `delta.tool_calls`, but split across many chunks (the name in one, the JSON
arguments a few characters at a time), so we join them by their `index` and
return the finished list.

> The earlier design made a **non-streaming** call first and only re-asked with
> `stream=True` when there were no tool calls. For a plain task like
> "Tell me a story" the model answers on that very first non-streaming call, so
> the text never streamed. Streaming *every* turn — and reading tool calls from
> the same stream — fixes that.

## Step 6 — Add the agent loop that streams every turn

Add the loop below the helper. Every turn goes through `stream_turn`, so text
always prints live. If the turn produced tool calls, we run them and loop again;
if it produced only text, we're done:

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
        text, tool_calls = stream_turn(messages)

        if not tool_calls:
            # Only text this turn — the answer already streamed above.
            return text

        # Record the assistant turn (text, if any, plus the tool calls).
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
                    "content": str(result),
                }
            )

    return "Stopped: reached the turn limit."
```

Notice the flow: `stream_turn` handles both jobs in one streamed call — printing
text as it flows and handing back any tool calls it collected. When a turn has
tool calls we rebuild the assistant message by hand (from the fragments we
stitched together) so the history stays valid, run each tool, and loop. When a
turn has only text, that text already streamed to the screen, so we simply return
it.

## Step 7 — Add the runner

`stream_turn` prints the answer itself, so the runner just calls the function.
Let's use a task that needs no tools at all — the purest test of streaming:

```python
if __name__ == "__main__":
    task = "Tell me a story"
    run_agent(task)
```

## Step 8 — Run it and watch the text flow

```powershell
python file_agent.py
```

"Tell me a story" needs no tools, so the model answers on the very first turn —
and because that turn streams, the story types itself out word by word:

```
bot> Once upon a time, in a valley wrapped in morning mist, there lived a
clockmaker who had never once been late. Every dawn she wound the great town
clock by hand...
```

Notice the *feel*: instead of a dead pause and then a wall of text, you watch the
answer being written. Because every turn streams, this works whether or not the
task needs tools.

## Step 9 — Try a task that uses the tools

Change the task to one that reads a file first:

```python
    task = "Read notes.txt and explain each point in a full sentence."
```

Run again:

```powershell
python file_agent.py
```

Now you'll see the tool line appear, followed by the streamed explanation:

```
    [turn 1] read_file({'filename': 'notes.txt'})
bot> The Monday meeting covered a possible March launch date. Bob has asked for
more testing before release. The budget is tight, so the extra ad spend will be
cut...
```

The tool line still prints on its own, and the final answer streams in after it —
because `stream_turn` handles both the tool-call turn and the text turn. Re-run
freely; it's safe.

## What you accomplished

You built a file agent with a live voice. The answer arrives token by token, so
the agent feels responsive even when the reply is long — and it streams on the
very first turn, even for a plain "Tell me a story" that touches no tools. You
learned that `stream=True` turns one response into a flow of `delta` chunks, that
text arrives at `delta.content` while tool calls arrive at `delta.tool_calls`
spread across chunks, and that streaming every turn (and stitching the tool-call
fragments back together) keeps the answer flowing no matter the task.

## Next steps

- Explore [Tutorial 7: Remember conversations across runs](../07-persist-the-conversation/07-persist-the-conversation.md),
  which saves the message history to disk so a session survives a restart.
- Want to *show* tool calls as they stream in, character by character, instead of
  printing them only once complete? You already collect the fragments in
  `stream_turn` — printing them live is a small extension of what you built.
