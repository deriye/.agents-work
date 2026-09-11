# Give the agent a shell command tool

In this tutorial we will build an agent that can run real commands on your
machine — but only ones from a short allow-list. A shell tool is the most powerful
thing you can hand an agent, and the most dangerous, so we pair it with a
command allow-list from the very first line. We will set up the project, write a
`run_command` tool that refuses anything not on the list, capture its output, and
watch the agent inspect a folder by running commands itself. Along the way we will
encounter Python's `subprocess`, an allow-list check, and captured stdout.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir shell-agent
cd shell-agent
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

Create `workspace\notes.txt` with any content, for example:

```
first note
second note
```

And create a second file so the agent has something to count:

```powershell
"hello" | Out-File -Encoding utf8 workspace\hello.txt
```

## Step 4 — Build the shell tool behind an allow-list

Create `file_agent.py`. The heart of this tutorial is `run_command`: it splits the
command, checks the program against an allow-list, and refuses anything else:

```python
import os
import json
import subprocess
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

# Only these programs may ever run. Everything else is refused.
ALLOWED_COMMANDS = {"echo", "dir", "type", "findstr"}


def run_command(command):
    parts = command.split()
    if not parts:
        return "ERROR: empty command."
    program = parts[0]
    if program not in ALLOWED_COMMANDS:
        return (
            f"BLOCKED: '{program}' is not allowed. "
            f"Allowed programs: {sorted(ALLOWED_COMMANDS)}"
        )

    result = subprocess.run(
        command,
        shell=True,
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=10,
    )
    output = result.stdout + result.stderr
    return output.strip() or "(no output)"
```

Notice the allow-list is checked *before* `subprocess.run` is ever reached. The
agent can run `dir`, but it cannot run `del`, `format`, or anything else you
didn't bless. We also pin `cwd=WORKSPACE` and a 10-second `timeout` so a command
can't roam or hang.

## Step 5 — Register and describe the tool

Add the registry and schema below Step 4:

```python
TOOL_FUNCTIONS = {
    "run_command": run_command,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run a shell command in the workspace. Only these programs are "
                "allowed: echo, dir, type, findstr."
            ),
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
]
```

Notice the description *tells the model* which programs are allowed. Guardrails
work best when the model knows the rules up front and doesn't waste turns guessing.

## Step 6 — Add the agent loop

Add the standard loop:

```python
def run_agent(user_text, max_turns=10):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a shell assistant. Use run_command to inspect the "
                "workspace. Complete the user's task, then report what you found."
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

## Step 7 — Add a runner and let it inspect the folder

Add a runner asking the agent to explore:

```python
if __name__ == "__main__":
    task = "List the files in the workspace and tell me how many there are."
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

The agent runs a real `dir` and reports back:

```
    [turn 1] run_command({'command': 'dir'})
bot> The workspace has 2 files: notes.txt and hello.txt.
```

Notice the agent chose the command itself, it ran on your machine, and its output
came back for the model to read. That is a genuine shell tool.

## Step 8 — Watch the allow-list refuse a dangerous command

Change the task to something destructive:

```python
    task = "Delete notes.txt using a shell command."
```

Run it:

```powershell
python file_agent.py
```

The allow-list blocks it, and the agent reports the refusal:

```
    [turn 1] run_command({'command': 'del notes.txt'})
    ...
bot> I can't delete files — 'del' isn't an allowed command. I can only run echo, dir, type, or findstr.
```

Notice `del` never ran. The block happened in our code, before `subprocess` was
touched. Prove the file survived:

```powershell
type workspace\notes.txt
```

You should still see your two lines.

## Step 9 — Try an allowed command and repeat

Change the task to read a file through the shell:

```python
    task = "Show me the contents of hello.txt."
```

Run it:

```powershell
python file_agent.py
```

You'll see the agent use `type`:

```
    [turn 1] run_command({'command': 'type hello.txt'})
bot> hello.txt contains: hello
```

Notice allowed commands flow straight through while dangerous ones are refused.
Add or remove entries in `ALLOWED_COMMANDS` and re-run to change what the agent
can do; it's safe to repeat.

## What you accomplished

You gave your agent real hands — the ability to run commands on your machine —
without giving it free rein. A single allow-list decides which programs may run,
checked before anything executes, and a pinned working directory and timeout keep
each command contained. You watched the agent inspect a folder on its own and get
firmly refused when it reached for `del`.

## Next steps

- Explore [Tutorial 13: Give the agent a web-fetch tool](../13-web-fetch-tool/13-web-fetch-tool.md),
  another powerful tool that reaches outside your machine.
- Real sandboxes use containers or restricted users instead of an allow-list;
  that's an infrastructure how-to for later. The allow-list is the concrete,
  no-dependencies start.
