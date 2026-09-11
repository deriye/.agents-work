# Give the agent a plan it follows

In this tutorial we will make the agent think before it acts. Instead of jumping
straight to tools, it first calls a `write_plan` tool to lay out numbered steps,
then works through them, updating the plan as it goes. This "reason, then act"
pattern is called ReAct. We will set up the project, build a file agent, add a
plan tool that stores and prints the current plan, and watch the agent draft a
plan and follow it. Along the way we will encounter a stored plan, a system prompt
that demands one first, and visible steps checked off as work proceeds.

> The reason-and-act pattern comes from the ReAct paper: <https://arxiv.org/abs/2210.03629>.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir plan-agent
cd plan-agent
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

## Step 3 — Make a sandbox folder with a file

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

## Step 4 — Build the file tools

Create `file_agent.py` with the usual file tools:

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


def write_file(filename, content):
    with open(os.path.join(WORKSPACE, filename), "w", encoding="utf-8") as f:
        f.write(content)
    return f"wrote {len(content)} characters to {filename}"
```

## Step 5 — Add the plan tool

This is the heart of the tutorial. `write_plan` takes the agent's numbered steps,
stores them, prints them so we can watch, and confirms back to the model:

```python
CURRENT_PLAN = []


def write_plan(steps):
    CURRENT_PLAN.clear()
    CURRENT_PLAN.extend(steps)
    print("    --- plan ---")
    for i, step in enumerate(CURRENT_PLAN, 1):
        print(f"    {i}. {step}")
    print("    ------------")
    return f"Plan saved with {len(CURRENT_PLAN)} steps. Now carry it out."
```

Notice the plan isn't just talk — it's a real tool call with a real result. The
agent must produce a concrete list, and we can see exactly what it committed to
before any file is touched.

## Step 6 — Register the tools

Add the registry and schemas. `write_plan` takes an array of strings:

```python
TOOL_FUNCTIONS = {
    "write_plan": write_plan,
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "write_plan",
            "description": "Record a numbered plan of steps before doing the work.",
            "parameters": {
                "type": "object",
                "properties": {
                    "steps": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["steps"],
            },
        },
    },
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

## Step 7 — Demand a plan in the system prompt

Add the loop. The one new idea is the system prompt: it *requires* a plan before
any other tool:

```python
def run_agent(user_text, max_turns=12):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful file assistant. Before doing anything else, "
                "call write_plan with your numbered steps. Then work through the "
                "plan using the file tools, one step at a time. When every step "
                "is done, report what you did."
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
            if name != "write_plan":
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

Notice the prompt makes planning the *first* required action. The agent can't skip
straight to reading and writing; it has to commit to steps first.

## Step 8 — Give it a multi-part task and watch it plan

Add a runner with a task that has clear stages:

```python
if __name__ == "__main__":
    task = (
        "Read notes.txt, then write a file called summary.txt containing a "
        "one-line summary and the date of the next meeting."
    )
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

The agent lays out a plan first, then executes it step by step:

```
    --- plan ---
    1. Read notes.txt to see its contents.
    2. Write summary.txt with a one-line summary and the next meeting date.
    3. Report what was done.
    ------------
    [turn 2] read_file({'filename': 'notes.txt'})
    [turn 3] write_file({'filename': 'summary.txt', 'content': 'Summary: March release needs more testing; budget tight. Next meeting: Friday 2pm.'})
bot> I planned three steps, read notes.txt, and wrote summary.txt with a one-line summary and the next meeting (Friday 2pm).
```

Notice the plan appeared *before* any file was touched, and the following tool
calls follow the plan in order. Confirm the file was written:

```powershell
type workspace\summary.txt
```

You should see the one-line summary and the Friday 2pm meeting.

## Step 9 — Change the task and watch a new plan

Give it a different multi-step job and run again:

```python
    task = "Count how many lines notes.txt has and save that number to count.txt."
```

```powershell
python file_agent.py
```

```
    --- plan ---
    1. Read notes.txt and count its lines.
    2. Write the count to count.txt.
    3. Report the result.
    ------------
    [turn 2] read_file({'filename': 'notes.txt'})
    [turn 3] write_file({'filename': 'count.txt', 'content': '5'})
bot> I planned it out, counted 5 lines in notes.txt, and saved 5 to count.txt.
```

Notice the agent drafted a fresh plan for the new task and followed it in order
again. The plan-first habit holds whatever you ask. Change the task and re-run;
it's safe to repeat.

## What you accomplished

You taught your agent to reason before it acts. A required `write_plan` tool forces
it to commit to numbered steps first, stores and prints them, and then the agent
works through the file tools in that order — the ReAct pattern in miniature. You
watched it draft a plan before touching a file, follow the steps, and produce a
fresh plan the moment the task changed.

## Next steps

- Re-visit the [ReAct paper](https://arxiv.org/abs/2210.03629) to see the reasoning
  traces this pattern is modelled on.
- Having the agent tick off or rewrite the plan after each step, so the plan tracks
  progress live, is a natural extension for later. A committed plan up front is the
  concrete start.
