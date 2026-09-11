# Generate tool schemas from your functions

In this tutorial we will stop hand-writing the big JSON `tools` list and generate
it automatically from the Python functions themselves. Every tool is just a
function with type hints and a docstring, so we can read those with `inspect` and
build the schema the API expects. We will set up the project, write three file
tools with type hints, write a `build_schema` helper that turns any function into
a tool definition, and watch the agent work with schemas nobody typed by hand.
Along the way we will encounter `inspect.signature`, a type-hint-to-JSON mapping,
and the docstring becoming the tool description.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir schema-agent
cd schema-agent
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

Create `workspace\notes.txt` with a few lines, for example:

```
meeting monday about the march release
bob wants more testing before we ship
budget is tight this quarter
next meeting friday 2pm
remember: update the changelog
```

## Step 4 — Write the tools with type hints and docstrings

Create `file_agent.py`. Write the three file tools first — notice each parameter
has a type hint and each function has a one-line docstring, because those are what
we will turn into a schema:

```python
import os
import json
import inspect
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


def list_files() -> str:
    """List the files in the workspace."""
    return "\n".join(os.listdir(WORKSPACE)) or "(empty)"


def read_file(filename: str) -> str:
    """Read the contents of a file in the workspace."""
    with open(os.path.join(WORKSPACE, filename), "r", encoding="utf-8") as f:
        return f.read()


def write_file(filename: str, content: str) -> str:
    """Write text to a file in the workspace."""
    with open(os.path.join(WORKSPACE, filename), "w", encoding="utf-8") as f:
        f.write(content)
    return f"wrote {len(content)} characters to {filename}"
```

## Step 5 — Build the schema from a function

This is the heart of the tutorial. `build_schema` reads a function's signature and
docstring and produces the exact tool definition the API wants — no hand-written
JSON:

```python
PYTHON_TO_JSON = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}


def build_schema(func):
    sig = inspect.signature(func)
    properties = {}
    required = []
    for name, param in sig.parameters.items():
        json_type = PYTHON_TO_JSON.get(param.annotation, "string")
        properties[name] = {"type": json_type}
        required.append(name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }
```

Notice how the pieces line up: the function name becomes the tool name, the
docstring becomes the description, each parameter becomes a property, and its type
hint is mapped to a JSON type through `PYTHON_TO_JSON`.

## Step 6 — Register the tools and generate the schema list

Now the registry is the *only* place we list our tools. The schema list is
generated from it:

```python
TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
}

tools = [build_schema(func) for func in TOOL_FUNCTIONS.values()]
```

Notice there is no hand-typed `tools` block anywhere. Adding a new tool now means
writing one function and adding one line to `TOOL_FUNCTIONS` — the schema follows
for free.

## Step 7 — Prove the generated schema is correct

Before the agent loop, add a quick check so we can *see* what `build_schema`
produced:

```python
if __name__ == "__main__":
    print(json.dumps(tools[1], indent=2))
```

Run it:

```powershell
python file_agent.py
```

You should see the schema for `read_file`, built entirely from its signature and
docstring:

```
{
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "Read the contents of a file in the workspace.",
    "parameters": {
      "type": "object",
      "properties": {
        "filename": {
          "type": "string"
        }
      },
      "required": [
        "filename"
      ]
    }
  }
}
```

Notice the description is the docstring and the `filename` property is `string`
because its type hint is `str` — all derived, none typed by hand.

## Step 8 — Add the agent loop

Replace that temporary `__main__` block with the standard loop plus a runner:

```python
def run_agent(user_text, max_turns=10):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful file assistant. You can list, read, and write "
                "files in the workspace. Complete the user's task, then report "
                "what you did."
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


if __name__ == "__main__":
    task = "Read notes.txt and tell me the single most important action item."
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

The agent uses the generated schema to call `read_file` and answers:

```
    [turn 1] read_file({'filename': 'notes.txt'})
bot> The most important action item is to do more testing before shipping, since Bob wants that before the March release.
```

Notice the agent never knew the schema was generated — it works exactly as if you
had typed the JSON, because `build_schema` produced the same shape.

## Step 9 — Add a fourth tool with one line and repeat

Prove the payoff. Add a new tool function above the registry:

```python
def count_lines(filename: str) -> str:
    """Count the lines in a file in the workspace."""
    with open(os.path.join(WORKSPACE, filename), "r", encoding="utf-8") as f:
        return f"{len(f.readlines())} lines"
```

Add just one line to the registry:

```python
TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "count_lines": count_lines,
}
```

Change the task and run again:

```python
    task = "How many lines are in notes.txt?"
```

```powershell
python file_agent.py
```

```
    [turn 1] count_lines({'filename': 'notes.txt'})
bot> notes.txt has 5 lines.
```

Notice you added a whole tool without writing a single line of JSON schema. The
generator picked it up automatically.

## What you accomplished

You made your tool definitions write themselves. `build_schema` reads a function's
signature, type hints, and docstring and produces the exact JSON the API expects,
so `TOOL_FUNCTIONS` is now the one and only list of your tools. You saw the
generated schema match a hand-written one, watched the agent use it, and added a
brand-new tool with a single registry line.

## Next steps

- Explore [Tutorial 15: Keep the conversation from growing forever](../15-context-management/15-context-management.md),
  which stops long runs from overflowing the model's context.
- Supporting optional parameters, enums, or nested objects in the generator are
  refinements for later. The signature-to-schema core is the idea.
