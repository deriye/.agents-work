# Complete a multi-step task

In this tutorial we will give our agent real hands: tools to list files, read a
file, and write a file. Then we'll set it a genuine multi-step job — read a file
of raw notes and write a tidy summary to a new file — and watch it plan and act
across several turns. Along the way we will encounter file-system tools, a
working directory to keep the agent safe, and a turn limit that stops runaway
loops.

This is a complete, if small, agent harness.

## Prerequisites

- You have finished [Tutorial 3](./03-agent-loop.md) and `agent_loop.py` works.
- Your `.venv` is active and your `.env` file from Tutorial 0 is in the folder
  you run scripts from.

## Step 1 — Make a sandbox folder for the agent to work in

We keep the agent's file operations inside one folder so it can't touch anything
else. Create it now:

```powershell
mkdir workspace
```

Now create a file `workspace\notes.txt` with some raw notes in it. Put exactly
this content in it:

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

You should see the five lines you just wrote printed back.

## Step 2 — Start the harness file with safe file tools

Create a file called `file_agent.py`. First the client setup and the three file
tools, each locked to the `workspace` folder:

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

Notice `_safe_path`: it forces every filename back inside `workspace`. This is
the guardrail that keeps an autonomous agent from writing anywhere it likes.

## Step 3 — Register the tools and describe them

Add the registry and schemas below Step 2:

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

## Step 4 — Reuse the agent loop, now with a turn limit

This loop is the one from Tutorial 3, with one addition: a `max_turns` guard so
the agent can never spin forever. Add:

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
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"  [turn {turn + 1}] {name}({args})")

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

Notice the only real change from Tutorial 3 is `for turn in range(max_turns)`
instead of `while True`. Autonomy is good; unbounded autonomy is a hang.

## Step 5 — Give it the real task

Add the runner at the bottom:

```python
if __name__ == "__main__":
    task = (
        "Read notes.txt, then write a clean bullet-point summary of the key "
        "points and action items to a new file called summary.txt."
    )
    result = run_agent(task)
    print("bot>", result)
```

Notice this one instruction forces a chain: the agent must *list or read* to
find the notes, *read* their contents, and *write* a new file — at least three
tool calls across several turns.

## Step 6 — Run it and watch the agent work

```powershell
python file_agent.py
```

You'll see the agent take several turns, then report back, something like:

```
  [turn 1] read_file({'filename': 'notes.txt'})
  [turn 2] write_file({'filename': 'summary.txt', 'content': '- Launch...'})
bot> I read notes.txt and wrote a summary to summary.txt with the key points and action items.
```

Notice the turns are numbered, so you can *see* the agent planning: it read
first, then wrote. It decided that order on its own — we never told it to read
before writing.

If you see `Stopped: reached the turn limit.`, the agent got stuck in a loop;
just run it again, and it will usually finish well within the limit.

## Step 7 — Check the agent's work

The real proof is the new file. Look at what it produced:

```powershell
type workspace\summary.txt
```

You should see a tidy summary, something like:

```
- Launch date discussed, possibly March
- Bob wants more testing before release
- Budget is tight; cut extra ad spend
- Action: schedule next meeting Friday 2pm
- Action: update the changelog
```

The exact wording will vary, but it should be a clean summary of *your* notes.
Notice that the agent read a file you wrote and produced a new file with no
further help from you. That's a harness doing a real job.

## Step 8 — Give it a new task and repeat

Change `task` in Step 5 to something new — for example:

```python
    task = "List the files in the workspace, then tell me which one is largest."
```

Save and run again:

```powershell
python file_agent.py
```

Notice the agent now reaches for `list_files` first instead of `read_file`,
because the task calls for it. Same harness, different plan. Re-run with as many
tasks as you like — reading and listing are safe to repeat, and writing simply
overwrites the target file.

## What you accomplished

You built a small but complete agent harness. It has a set of real tools, a
safety guardrail that pins file access to a sandbox, an autonomous loop with a
turn limit, and it completed a genuine multi-step task: reading your notes and
writing a summary, deciding the order of operations by itself. Everything you
learned across the series — the request, the message history, tool schemas, the
tool-result round trip, and the loop — comes together here.

## Next steps

You now have a working foundation. When you want to grow it into something
larger, these are the natural directions — each is a *how-to* or *explanation*
topic rather than a tutorial, so reach for them when you have a specific goal:

- Add streaming so replies appear token by token.
- Add more tools (run a shell command, call a web API, query a database).
- Persist the conversation to disk so sessions survive restarts.
- Handle tool errors gracefully by returning the error text as the tool result
  so the agent can recover.
- Read about the ReAct pattern that underpins tool-using agents:
  <https://arxiv.org/abs/2210.03629>.

You've built your own agent harness from nothing. Come back to it, break it,
extend it — that's how it becomes yours.
