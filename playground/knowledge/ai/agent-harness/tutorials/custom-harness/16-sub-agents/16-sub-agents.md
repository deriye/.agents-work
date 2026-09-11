# Delegate work to a sub-agent

In this tutorial we will let one agent hand a focused job to another. The main
agent stays high-level and calls a `delegate` tool; that tool spins up a fresh
inner agent — its own message list, its own tool loop — to do the detailed work
and return only its final answer. We will set up the project, build a small file
agent, wrap a second copy of the loop as a delegate tool, and watch the outer
agent farm out a task and get back a clean result. Along the way we will encounter
a nested agent loop, a summarised result instead of raw tool chatter, and a clear
boundary between planner and worker.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir subagent-agent
cd subagent-agent
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

## Step 3 — Make a sandbox folder with a couple of files

```powershell
mkdir workspace
```

Create `workspace\notes.txt` with a few lines:

```
meeting monday about the march release
bob wants more testing before we ship
budget is tight this quarter
next meeting friday 2pm
remember: update the changelog
```

And a second file for the worker to find:

```powershell
"ticket-42: fix the login crash" | Out-File -Encoding utf8 workspace\tasks.txt
```

## Step 4 — Build the worker's file tools

Create `file_agent.py`. Start with the low-level tools the *worker* will use:

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
```

## Step 5 — Write the worker loop

Add a small self-contained loop for the worker. It's the same shape as any agent
loop — its own `messages`, its own tools — and it returns a single final string:

```python
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
```

Notice the worker has its own conversation. Nothing it does — the files it lists,
the tools it calls — leaks back to whoever called it. Only its final sentence does.

## Step 6 — Expose the worker as a `delegate` tool

This is the heart of the tutorial. The *only* tool the main agent gets is
`delegate`, which simply runs a worker on the subtask and hands back its answer:

```python
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
```

Notice the main agent has *no* file tools at all. It can't read a file itself; it
can only delegate. That is the whole point — the planner stays high-level and the
worker does the digging.

## Step 7 — Write the main loop

Add the outer loop. It's the standard shape, but its tools are `main_tools`:

```python
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
```

## Step 8 — Give it a job and watch it delegate

Add a runner:

```python
if __name__ == "__main__":
    task = "Find out what ticket is in tasks.txt and what the notes say the next meeting is."
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

The main agent delegates the digging and reports the combined result:

```
    [turn 1] delegate({'task': 'Read tasks.txt and report the ticket it contains.'})
      -> delegating: Read tasks.txt and report the ticket it contains.
      <- worker done
    [turn 2] delegate({'task': 'Read notes.txt and report when the next meeting is.'})
      -> delegating: Read notes.txt and report when the next meeting is.
      <- worker done
bot> tasks.txt holds ticket-42 (fix the login crash), and notes.txt says the next meeting is Friday at 2pm.
```

Notice the outer agent never saw the file contents — only each worker's one-line
answer. The detailed reading happened inside a separate conversation and came back
summarised.

## Step 9 — Change the job and repeat

Give it a different delegation and run again:

```python
    task = "Ask a worker how many files are in the workspace, then tell me."
```

```powershell
python file_agent.py
```

```
    [turn 1] delegate({'task': 'List the workspace files and count them.'})
      -> delegating: List the workspace files and count them.
      <- worker done
bot> A worker checked the workspace and found 2 files.
```

Notice the same delegate boundary handles a completely different subtask. The main
agent phrases the job, the worker does it, the answer comes back clean. Change the
task and re-run; it's safe to repeat.

## What you accomplished

You split your agent into a planner and a worker. The main agent has no file tools
at all — it can only `delegate`, which runs a fresh sub-agent with its own
conversation and its own tools, then returns just the worker's final answer. You
watched the lead farm out two subtasks, stay ignorant of the raw file contents, and
still deliver a clean combined result.

## Next steps

- Explore [Tutorial 17: Give the agent a plan it follows](../17-structured-planning-react/17-structured-planning-react.md),
  which has a single agent lay out and track its own steps.
- Running several workers in parallel, or giving each a different tool set, are
  scaling ideas for later. One planner and one worker is the concrete start.
